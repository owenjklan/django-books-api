from typing import Any, Callable

from django.db.models import Model

from ninja import ModelSchema
from ninja.orm import create_schema

from autodojo.constants import SPECIAL_METHODS_TRANSLATION


class AutoDojoViewGenerator:
    """
    Base class for HTTP method-specific generator classes.
    """

    def __init__(
        self,
        model_class: Model,
        http_method: str,
        request_schema: ModelSchema = None,
        response_schema: ModelSchema = None,
        request_schema_config: dict[str, Any] = None,
        response_schema_config: dict[str, Any] = None,
    ) -> None:
        self.model_class: Model = model_class
        self.model_class_name: str = self.model_class._meta.object_name
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.request_schema_config = (
            request_schema_config if request_schema_config is not None else {}
        )
        self.response_schema_config = (
            response_schema_config if response_schema_config is not None else {}
        )
        self.http_method = http_method

    def generate_request_schema(
        self,
    ) -> ModelSchema:
        """
        Generate a schema to be used for incoming request payloads but catches
        attempts to generate a schema in situations where one was explicitly
        supplied.
        """
        if self.request_schema:
            raise RuntimeError(
                "Refusing to generate request schema when existing schema was supplied!"
            )

        schema_config = self._determine_request_schema_config()

        self.request_schema = create_schema(self.model_class, **schema_config)
        return self.request_schema

    def generate_response_schema(
        self,
    ) -> ModelSchema:
        """
        Generate a schema to be used for outgoing response payloads but catches
        attempts to generate a schema in situations where one was explicitly
        supplied.
        """
        if self.response_schema_config:
            raise RuntimeError(
                "Refusing to generate response schema when existing schema was supplied!"
            )

        schema_config = self._determine_response_schema_config()

        self.response_schema = create_schema(self.model_class, **schema_config)
        return self.response_schema

    def patch_view_signature(self, view_func: Callable) -> Callable:
        """
        Programmatically-generated view functions can specify parameter
        names, like 'payload' for example, but because the input schema
        definitions aren't known until run-time, we may need to adjust
        the generated view function's signature, updating the type
        annotations to use our generated classes. Otherwise, Django Ninja
        won't be able to supply the correct payloads.

        Default implementation makes no changes.
        """
        return view_func

    def _determine_request_schema_config(self) -> dict[str, Any]:
        # The create_schema() call won't accept None for the
        # kwargs dict, so we need an actual dictionary
        schema_config = {}

        # Setup generator-specific defaults, if present
        if hasattr(self, "default_request_schema_config"):
            if not isinstance(self.default_request_schema_config, dict):
                raise TypeError(
                    f"{self.__class__.__name__}.default_request_schema_config must be a dict"
                )

            schema_config = self.default_request_schema_config.copy()

            # Now apply schema configs that may have been supplied by
        # the user
        if self.request_schema_config:
            for key, value in self.request_schema_config.items():
                schema_config[key] = value

        # Double-check for a defined 'name'. If not provided by
        # defaults or user-supplied configuration, then we'll
        # automatically generate one. Note that if the name WAS
        # provided by defaults or user configuration, we'll treat
        # it as a format string and supply 'model' and 'http_verb'.
        http_verb = SPECIAL_METHODS_TRANSLATION.get(
            self.http_method, self.http_method
        ).title()
        if "name" not in schema_config:
            schema_config["name"] = f"Generated{self.model_class_name}{http_verb}In"
        else:
            schema_config["name"] = schema_config["name"].format(
                model=self.model_class_name, http_verb=http_verb
            )

        return schema_config

    def _determine_response_schema_config(self) -> dict[str, Any]:
        # The create_schema() call won't accept None for the
        # kwargs dict, so we need an actual dictionary
        schema_config = {}

        # Setup generator-specific defaults, if present
        if hasattr(self, "default_response_schema_config"):
            if not isinstance(self.default_response_schema_config, dict):
                raise TypeError(
                    f"{self.__class__.__name__}.default_response_schema_config must be a dict"
                )
            schema_config = self.default_response_schema_config.copy()

        # Now apply schema configs that may have been supplied by
        # the user
        if self.request_schema_config:
            for key, value in self.request_schema_config.items():
                schema_config[key] = value

        # Double-check for a defined 'name'. If not provided by
        # defaults or user-supplied configuration, then we'll
        # automatically generate one. Note that if the name WAS
        # provided by defaults or user configuration, we'll treat
        # it as a format string and supply 'model' and 'http_verb'.
        http_verb = SPECIAL_METHODS_TRANSLATION.get(
            self.http_method, self.http_method
        ).title()
        if "name" not in schema_config:
            schema_config["name"] = f"Generated{self.model_class_name}{http_verb}Out"
        else:
            schema_config["name"] = schema_config["name"].format(
                model=self.model_class_name, http_verb=http_verb
            )

        return schema_config
