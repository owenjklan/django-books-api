from django.db.models.fields.related import ForeignKey
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.helpers import patch_object, delete_object
from books_api.models import Book, Publisher
from books_api.schemas import (
    BookOutSchema,
    BookInSchema,
    BookOutSubSchema,
    BookInPatchSchema,
)

router = Router(tags=["Books"])


@router.get("/", response=list[BookOutSchema])
def get_books(request: HttpRequest) -> JsonResponse:
    books = Book.objects.all()
    return books


@router.get("/{int:book_id}", response=BookOutSchema)
def get_book(request: HttpRequest, book_id: int) -> JsonResponse:
    book = get_object_or_404(Book, pk=book_id)
    return book


@router.post("/", response=BookOutSchema)
def add_book(request: HttpRequest, book: BookInSchema) -> JsonResponse:
    new_book = Book.objects.create(**book.dict())

    return new_book


@router.put("/{int:book_id}", response=BookOutSchema)
def update_book(request: HttpRequest, book_id: int, book: BookInSchema) -> JsonResponse:
    updated_book = Book.objects.update(pk=book_id, **book.dict())
    return updated_book


@router.patch("/{int:book_id}", response=BookOutSchema)
def patch_book(
    request: HttpRequest, book_id: int, book: BookInPatchSchema
) -> JsonResponse:
    response_code, response_dict = patch_object("books_api", "Book", book_id, book)

    return JsonResponse(status=response_code, data=response_dict)


@router.delete("/{int:book_id}")
def delete_book(request: HttpRequest, book_id: int) -> JsonResponse:
    response_code, response_dict = delete_object("Book", book_id)
    return JsonResponse(status=response_code, data=response_dict)
