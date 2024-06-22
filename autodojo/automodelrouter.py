import ninja
from django.apps import apps
from django.db import models
from ninja import ModelSchema
from ninja.orm import create_schema

from autodojo.viewfuncs import (
    generate_get_list_view_func,
    generate_patch_view_func,
    patch_view_signature,
)

#
# router = Router(tags=["Authors"])
#
#
# @router.get("/", response={200: list[AuthorOutSchema]})
# def get_authors(request: HttpRequest):
#     authors = Author.objects.all()
#     return 200, authors


# Registry for auto-generated view paths, their auto-generated
# input and output Schema classes
_path_registry: dict[str, dict] = {}


class AutoDojoView:
    def __init__(
        self,
        path,
    ):
        self.path = path


class AutoDojoRouter:
    def __init__(
        self,
        *,
        app_label: str = None,
        model: str | models.Model = None,
        auth_class: type = None,
    ):
        """

        :param app_label:
        :param model:
        """
        # Despite the kwargs all having defaults, the following args MUST be non-None.
        # The reason the signature is like this is so the call can be somewhat self-describing
        required_kwargs = ["app_label", "model"]
        self._enforce_required_kwargs(locals(), required_kwargs)

        self.app_label = (
            app_label  # Must be set before _resolve_orm_model_class() is called
        )
        self.model_class = self._resolve_orm_model_class(model)

        # Automatically create the Ninja ModelSchema classes
        # TODO: This should be HTTP-verb specific, also tracking generated path
        self.out_schema_class = create_schema(
            self.model_class
        )  # generate_simple_out_schema(self.model_class)

        # Things we might add to the Router
        self.auth_class = auth_class

        self.base_url_path = f"/{self.model_class._meta.object_name.lower()}/"
        self.get_list_view_func = generate_get_list_view_func(self.model_class)

        # Now, let's wire everything up in the router
        self.router = ninja.Router()
        self.router.add_api_operation(
            f"/",
            methods=["GET"],
            response={200: list[self.out_schema_class]},
            view_func=self.get_list_view_func,
            tags=[self.model_class._meta.object_name],
        )

        self.patch_in_schema = create_schema(
            self.model_class,
            name=f"Generated{self.model_class._meta.object_name}PatchInSchema",
            optional_fields="__all__",
            exclude=["id"],
        )

        self.patch_view_func = generate_patch_view_func(
            self.model_class, self.patch_in_schema
        )
        self.patch_view_func = patch_view_signature(
            self.patch_view_func, self.patch_in_schema
        )

        self.router.add_api_operation(
            "/{int:id}",
            methods=["PATCH"],
            response={200: self.out_schema_class},
            view_func=self.patch_view_func,
            tags=[self.model_class._meta.object_name],
        )

    def get_router(self) -> ninja.Router:
        return self.router

    def _enforce_required_kwargs(
        self, called_args: dict, required_kwargs: list[str]
    ) -> None:
        for arg, value in called_args.items():
            if arg not in required_kwargs:
                continue

            if value is None:
                raise ValueError(f"'{arg}' cannot be None")

    def _resolve_orm_model_class(self, model: str | models.Model) -> models.Model:
        if isinstance(model, models.Model):
            return model

        if not isinstance(model, str):
            raise ValueError(f"'{model}' is not a string or ORM Model class")

        # Look-up the class from Django's Apps configurations
        model_class = apps.get_model(self.app_label, model)
        return model_class
