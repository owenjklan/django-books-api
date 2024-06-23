from typing import Callable, Any, Optional

from django.http import HttpRequest

from autodojo.generators.base_classes import AutoDojoViewGenerator
from autodojo.generators.utility import ensure_unique_name


class AutoDojoGetListGenerator(AutoDojoViewGenerator):
    """
    Generator for GET all (ie: List all) endpoint
    """

    def generate_view_func(self) -> Callable:
        def get_list_view_func(request: HttpRequest, *args, **kwargs):
            object_collection = self.model_class.objects.all()
            return 200, object_collection

        returned_func = ensure_unique_name(self.model_class, get_list_view_func)

        return returned_func

    @property
    def url_path(self) -> str:
        return "/"

    @property
    def response_config(self) -> dict[int, Optional[Any]]:
        return {200: list[self.response_schema]}
