from django.http import JsonResponse, HttpRequest
from ninja import Router


router = Router(tags=["Categories"])


@router.get("/")
def get_categories(request: HttpRequest) -> JsonResponse:
    return "GET Categories"


@router.get("/{int:category_id}")
def get_category(request: HttpRequest, category_id: int) -> JsonResponse:
    return JsonResponse({"category_id": category_id})
