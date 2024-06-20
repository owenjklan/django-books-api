from django.http import JsonResponse, HttpRequest
from ninja import Router


router = Router(tags=["Authors"])


@router.get("/")
def get_authors(request: HttpRequest) -> JsonResponse:
    return "GET Authors"


@router.get("/{int:author_id}")
def get_author(request: HttpRequest, author_id: int) -> JsonResponse:
    return JsonResponse({"author_id": author_id})
