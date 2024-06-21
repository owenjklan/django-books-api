from typing import Optional

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models.fields.related import ForeignKey
from django.forms import model_to_dict
from ninja import ModelSchema


def validate_schema_fk_references(
    model_class: Model, payload: ModelSchema
) -> tuple[int, Optional[dict]]:
    """
    Inspect the supplied schema object to ensure that any
    foreign keys are explicitly included as {field_name}_id.
    If provided as {field_name}, then Ninja will drop them
    from the schema and resultant dict. This means they
    become a silent no-op. Rather than hide this fact, we'll
    opt to complain that the supplied key won't work as expected.

    If everything is fine, then 200, None is returned. Otherwise,
    400 and a dictionary containing the error response details is
    returned.
    """
    # Get the target model's FK field names
    field_list = model_class._meta.get_fields()
    fk_field_names = set(
        [field.name for field in field_list if isinstance(field, ForeignKey)]
    )

    # Make a note of the possible fields to the schema that weren't
    # even set on input. This allows us to catch differences in
    # supplied fields vs. excluded fields.
    schema_supplied_fields = []

    # Now, convert the supplied payload Schema to a dictionary and
    # any fields that are foreign keys on the ORM model, but absent
    # in the dict, have been supplied in the payload without the "_id"
    # suffix. Set 'exclude_unset=True', which is the behaviour used
    # by the object helpers (esp. patch_object())
    payload_dict = payload.dict(exclude_unset=True)

    ignored_fk_fields = [f for f in fk_field_names if f not in payload_dict.keys()]

    # Now inspect the fields that were set on the supplied payload schema
    # For each ignored field, if that field's name is not in payload.model_fields_set,
    # then we remove it from the list.
    for field in ignored_fk_fields:
        if field not in payload.model_fields_set:
            ignored_fk_fields.remove(field)

    if ignored_fk_fields:
        message = f"Foreign key fields were provided without '_id' suffix! Problem fields: {', '.join(ignored_fk_fields)}"
        return 400, {"success": False, "message": message}
    else:
        return 200, None


def patch_object(
    app_label: str, model_name: str, pk: int, payload: ModelSchema
) -> tuple[int, dict]:
    """
    Re-usable helper for patching objects, updating only supplied fields.

    Returns HTTP response code and response dictionary.

    If successful, 200 status will be returned and a dictionary of the updated
    object, suitable for JSON response.

    If the requested object doesn't, exist, then 404 status will be returned with
    an error message.
    """
    model_class = apps.get_model(app_label, model_name)

    status_code, error_dict = validate_schema_fk_references(model_class, payload)

    if error_dict is not None:
        return status_code, error_dict

    # Look up the object being modified, if it exists
    try:
        patched_object = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        return 404, {
            "success": False,
            "message": f"Requested {model_class.__class__} object does not exist",
        }

    patch_fields = payload.dict(exclude_unset=True)

    for attr, value in patch_fields.items():
        # Determine if the supplied attribute is a foreign key or not
        # Check for a field of the supplied attribute name
        field_meta = model_class._meta.get_field(attr)

        if field_meta.__class__ is ForeignKey:
            # Ninja appears to take  Model.fk_field and treat "fk_field" and "fk_field_id" the same.
            # For the purpose of reporting the attribute name, ensure it always ends with "_id" when
            # used in messages
            message_attr = attr if attr.endswith("_id") else f"{attr}_id"
            print(
                f"Foreign key attribute found on {model_class._meta.object_name} object: {message_attr}. Value: {value}"
            )
            related_model: Model
            try:
                related_model = field_meta.related_model
                related_model_name = related_model._meta.object_name
                referenced_object = related_model.objects.get(pk=value)
            except related_model.DoesNotExist:
                return 404, {
                    "success": False,
                    "message": f"{related_model_name} referenced by '{message_attr}' does not exist",
                }

            setattr(patched_object, attr, referenced_object)
        else:
            setattr(patched_object, attr, value)

    patched_object.save()
    patched_object.refresh_from_db()

    # Use Django's form helpers to translate ORM object to dict
    return 200, model_to_dict(patched_object)


def delete_object(model_name: str, pk: int) -> tuple[int, dict]:
    """
    For a model, specified by its name string, attempt to delete the
    instance with the supplied primary key. This assumes integer
    Primary Keys.

    Returns HTTP response code and response dictionary.

    If successful, 200 status will be returned.

    If the requested object doesn't, exist, then 404 status will be returned.
    """
