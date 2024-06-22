import decimal
from typing import Iterable, Callable

from django.apps import apps
from django.db import models
from django.db.models import Field, Model
from django.db.models.fields import CharField, TextField, DecimalField, BooleanField
from django.db.models.fields.related import ForeignKey
from django.http import HttpRequest, HttpResponse
from ninja import ModelSchema


def generate_get_list_view_func(model: models.Model) -> Callable:
    def get_list_view_func(request: HttpRequest, *args, **kwargs):
        object_collection = model.objects.all()
        return 200, object_collection

    returned_func = get_list_view_func

    # Make the name unique
    returned_func.__name__ = (
        f"{model._meta.object_name.lower()}_{returned_func.__name__}"
    )

    return returned_func


def generate_patch_view_func(
    model: models.Model, request_schema: ModelSchema
) -> Callable:
    def get_patch_view_func(
        request: HttpRequest, id: int, payload: ModelSchema, *args, **kwargs
    ):
        """
        Re-usable helper for patching objects, updating only supplied fields.

        Returns HTTP response code and response dictionary.

        If successful, 200 status will be returned and a dictionary of the updated
        object, suitable for JSON response.

        If the requested object doesn't, exist, then 404 status will be returned with
        an error message.
        """
        call_args = locals()
        # Look up the object being modified, if it exists
        try:
            patched_object = model.objects.get(pk=id)
        except model.DoesNotExist:
            return 404, {
                "api_error": f"Requested {model._meta.object_name} object does not exist",
            }

        patch_fields = payload.dict(exclude_unset=True)

        for attr, value in patch_fields.items():
            # Determine if the supplied attribute is a foreign key or not
            # Check for a field of the supplied attribute name
            field_meta = model._meta.get_field(attr)

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

    returned_func = get_patch_view_func

    # Make the name unique
    returned_func.__name__ = (
        f"{model._meta.object_name.lower()}_{returned_func.__name__}"
    )

    return returned_func


def patch_view_signature(view_func: Callable, payload_type: ModelSchema) -> Callable:
    vc = view_func
    view_func.__annotations__["payload"] = payload_type
    return view_func
