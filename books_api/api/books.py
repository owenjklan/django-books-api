from django.http import JsonResponse, HttpRequest
from ninja import Router

from ..models import Book
from ..schemas import BookSchema

router = Router(tags=["Books"])


@router.get("/", response=list[BookSchema])
def get_books(request: HttpRequest) -> JsonResponse:
    books = Book.objects.all()
    return books


@router.get("/{int:book_id}", response=BookSchema)
def get_book(request: HttpRequest, book_id: int) -> JsonResponse:
    book = Book.objects.get(id=book_id)
    return book


@router.post("/")
def add_book(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"book_id": 1})


@router.put("/{int:book_id}")
def update_book(request: HttpRequest, book_id: int) -> JsonResponse:
    return JsonResponse({"book_id": book_id})


@router.delete("/{int:book_id}")
def delete_book(request: HttpRequest, book_id: int) -> JsonResponse:
    return JsonResponse({"book_id": 1})
