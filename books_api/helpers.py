from typing import Optional

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db.models.fields.related import ForeignKey
from django.forms import model_to_dict
from ninja import ModelSchema, Schema


def patch_object(
    app_label: str, model_name: str, pk: int, payload: ModelSchema
) -> tuple[int, Model | Optional[dict]]:
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
            "api_error": f"Requested {model_class._meta.object_name} object does not exist",
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
            related_model: Model
            try:
                related_model = field_meta.related_model
                related_model_name = related_model._meta.object_name
                referenced_object = related_model.objects.get(pk=value)
            except related_model.DoesNotExist:
                return 404, {
                    "api_error": f"{related_model_name} referenced by '{message_attr}' does not exist",
                }

            setattr(patched_object, attr, referenced_object)
        else:
            setattr(patched_object, attr, value)

    patched_object.save()
    patched_object.refresh_from_db()

    return 200, patched_object


def delete_object(
    app_label: str, model_name: str, pk: int
) -> tuple[int, Model | Optional[dict]]:
    """
    For a model, specified by its name string, attempt to delete the
    instance with the supplied primary key. This assumes integer
    Primary Keys.

    Returns HTTP response code and response dictionary.

    If successful, 200 status will be returned.

    If the requested object doesn't, exist, then 404 status will be returned.
    """
    model_class = apps.get_model(app_label, model_name)

    try:
        deleted_object = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        return 404, {
            "api_error": f"Requested {model_class._meta.object_name} object does not exist",
        }

    deleted_object.delete()

    return 200, None  # Empty response body on successful delete


def update_object(
    app_label: str, model_name: str, pk: int, payload: ModelSchema
) -> tuple[int, Model | Optional[dict]]:
    model_class = apps.get_model(app_label, model_name)

    # Look up the object being modified, if it exists
    try:
        updated_object = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        return 404, {
            "api_error": f"Requested {model_class._meta.object_name} object does not exist",
        }

    patch_fields = payload.dict(exclude_unset=True)

    for attr, value in patch_fields.items():
        # Determine if the supplied attribute is a foreign key or not
        # Check for a field of the supplied attribute name
        field_meta = model_class._meta.get_field(attr)

        if field_meta.__class__ is ForeignKey:
            # Ninja appears to take  Model.fk_field and treat "fk_field" and "fk_field_id" the same.
            # For the purpose of reporting the attribute name, ensure it always ends with "_id" when
            # used in messages.
            message_attr = attr if attr.endswith("_id") else f"{attr}_id"
            related_model: Model
            try:
                related_model = field_meta.related_model
                related_model_name = related_model._meta.object_name
                referenced_object = related_model.objects.get(pk=value)
            except related_model.DoesNotExist:
                return 404, {
                    "api_error": f"{related_model_name} referenced by '{message_attr}' does not exist",
                }

            setattr(updated_object, attr, referenced_object)
        else:
            setattr(updated_object, attr, value)

    updated_object.save()
    updated_object.refresh_from_db()

    return 200, updated_object
