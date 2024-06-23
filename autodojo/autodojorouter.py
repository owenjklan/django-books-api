from typing import Callable, Any

import ninja
from django.apps import apps
from django.db import models


from autodojo.autodojoview import AutoDojoView

DEFAULT_METHODS = (
    "GET",
    "GETLIST",  # Special method to differentiate from get-single-object
    "POST",
    "PATCH",
    "PUT",
    "DELETE",
)

# Special methods, especially "GETLIST" 'just work' in terms of lookup
# for generator classes etc, but the HTTP method used will need to be
# translated.
SPECIAL_METHODS_TRANSLATION = {
    "GETLIST": "GET",
}


class AutoDojoRouter:
    def __init__(
        self,
        *,
        app_label: str = None,
        model: str | models.Model = None,
        http_methods: list[str] = DEFAULT_METHODS,
        auth_class: type = None,
    ):
        """ """
        # Despite the kwargs all having defaults, the following args MUST be non-None.
        # The reason the signature is like this is so the call can be somewhat self-describing
        required_kwargs = ["app_label", "model"]
        self._enforce_required_kwargs(locals(), required_kwargs)

        self.app_label = (
            app_label  # Must be set before _resolve_orm_model_class() is called
        )
        self.model_class = self._resolve_orm_model_class(model)
        self.model_class_name = self.model_class._meta.object_name

        # Things we might add to the Router
        self.auth_class = auth_class

        # The generated router will be "mounted" here in the urlpatterns
        self.base_url_path = f"/{self.model_class._meta.verbose_name_plural}/"

        # Now, let's wire everything up in the router
        self.router = ninja.Router()

        # Generate required method implementations
        # TODO: allow control/configuration of status-code specific
        #       response configurations.
        for http_method in http_methods:
            auto_view = AutoDojoView(self.model_class, http_method)

            # "GETLIST" in particular will need to be translated to "GET"
            actual_method_verb = SPECIAL_METHODS_TRANSLATION.get(
                http_method, http_method
            )

            self.router.add_api_operation(
                auto_view.url_path,
                methods=[actual_method_verb],
                response=auto_view.response_config,
                view_func=auto_view.view_func,
                tags=[self.model_class_name],
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
