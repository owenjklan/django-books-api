from typing import Any, Callable

from django.db.models import Model

from ninja import ModelSchema
from ninja.orm import create_schema


class AutoDojoViewGenerator:
    """
    Base class for HTTP method-specific generator classes.
    """

    def __init__(
        self,
        model_class: Model,
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
        self.request_schema = create_schema(
            self.model_class, **self.request_schema_config
        )
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
        self.response_schema = create_schema(
            self.model_class, **self.response_schema_config
        )
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
