from django.http import JsonResponse, HttpRequest
from ninja import Router


router = Router(tags=["Publishers"])


@router.get("/")
def get_publishers(request: HttpRequest) -> JsonResponse:
    return "GET Publishers"


@router.get("/{int:publisher_id}")
def get_publisher(request: HttpRequest, publisher_id: int) -> JsonResponse:
    return JsonResponse({"publishers_id": publisher_id})
