from django.http import JsonResponse, HttpRequest
from ninja import Router


router = Router(tags=["Books"])


@router.get("/")
def get_books(request: HttpRequest) -> JsonResponse:
    return "GET Books"


@router.get("/{int:book_id}")
def get_book(request: HttpRequest, book_id: int) -> JsonResponse:
    return JsonResponse({"book_id": book_id})
