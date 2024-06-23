from typing import Callable, Any, Optional

from django.http import HttpRequest
from ninja import Schema

from autodojo.generators.base_classes import AutoDojoViewGenerator
from autodojo.generators.utility import ensure_unique_name


class AutoDojoPostGenerator(AutoDojoViewGenerator):
    default_request_schema_config = {"exclude": ("id",), "name": "Generated{model}In"}
    default_response_schema_config = {"name": "Generated{model}Out"}

    def generate_view_func(self) -> Callable:
        def post_view_func(request: HttpRequest, payload: Schema, *args, **kwargs):
            new_object = self.model_class.objects.create(**payload.dict())
            return new_object

        returned_func = ensure_unique_name(self.model_class, post_view_func)
        return returned_func

    @property
    def url_path(self) -> str:
        return "/"

    @property
    def response_config(self) -> dict[int, Optional[Any]]:
        return {200: self.response_schema}

    def patch_view_signature(self, view_func: Callable) -> Callable:
        """
        To ensure that Ninja supplies our view with the appropriate payload
        schema object, we need to ensure the 'payload' argument is correctly
        annotated. This cannot be done until runtime, because we create
        the type (the ModelSchema) at runtime.
        """
        view_func.__annotations__["payload"] = self.request_schema
        return view_func
