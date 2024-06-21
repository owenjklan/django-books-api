from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models.fields.related import ForeignKey
from django.forms import model_to_dict
from ninja import ModelSchema


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
            print(
                f"Foreign key attribute found on {model_class.__class__} object: {attr}. Value: {value}"
            )
            related_model: Model
            try:
                related_model = field_meta.related_model
                referenced_object = related_model.objects.get(pk=value)
            except related_model.DoesNotExist:
                return 404, {
                    "success": False,
                    "message": f"{related_model.__class__} referenced by '{attr}' does not exist",
                }

            setattr(patched_object, attr, referenced_object)
        else:
            setattr(patched_object, attr, value)

    patched_object.save()

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
