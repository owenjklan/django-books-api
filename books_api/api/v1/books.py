from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.helpers import patch_object, delete_object, update_object
from books_api.models import Book
from books_api.schemas import (
    BookOutSchema,
    BookInSchema,
    BookInPatchSchema,
    ErrorSchema,
)

router = Router(tags=["Books"])


@router.get(
    "/", response={200: list[BookOutSchema], 400: ErrorSchema, 404: ErrorSchema}
)
def get_books(request: HttpRequest) -> JsonResponse:
    books = Book.objects.all()
    return books


@router.get(
    "/{int:book_id}", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema}
)
def get_book(request: HttpRequest, book_id: int) -> JsonResponse:
    book = get_object_or_404(Book, pk=book_id)
    return book


@router.post("/", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def add_book(request: HttpRequest, book: BookInSchema) -> JsonResponse:
    new_book = Book.objects.create(**book.dict())

    return new_book


@router.put(
    "/{int:book_id}", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema}
)
def update_book(request: HttpRequest, book_id: int, book: BookInSchema) -> JsonResponse:
    response_code, response_dict = update_object("books_api", "Book", book_id, book)

    return JsonResponse(status=response_code, data=response_dict)


@router.patch(
    "/{int:book_id}", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema}
)
def patch_book(
    request: HttpRequest, book_id: int, book: BookInPatchSchema
) -> JsonResponse:
    response_code, response_dict = patch_object("books_api", "Book", book_id, book)

    return JsonResponse(status=response_code, data=response_dict)


@router.delete("/{int:book_id}", response={200: None, 404: ErrorSchema})
def delete_book(request: HttpRequest, book_id: int) -> JsonResponse:
    response_code, response_dict = delete_object("books_api", "Book", book_id)
    return JsonResponse(status=response_code, data=response_dict)
