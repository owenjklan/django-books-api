from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.helpers import patch_object, delete_object, update_object
from books_api.models import Book, Author
from books_api.schemas import (
    BookOutSchema,
    BookInSchema,
    BookInPatchSchema,
    ErrorSchema,
    AuthorOutSchema,
    AuthorOutSubSchema,
    PrimaryKeyListSchema,
)

router = Router(tags=["Books"])


@router.get(
    "/", response={200: list[BookOutSchema], 400: ErrorSchema, 404: ErrorSchema}
)
def get_books(request: HttpRequest):
    books = Book.objects.all()
    return books


@router.get(
    "/{int:book_id}", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema}
)
def get_book(request: HttpRequest, book_id: int):
    book = get_object_or_404(Book, pk=book_id)
    return book


@router.post("/", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def add_book(request: HttpRequest, book: BookInSchema):
    new_book = Book.objects.create(**book.dict())
    return new_book


@router.put(
    "/{int:book_id}", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema}
)
def update_book(request: HttpRequest, book_id: int, book: BookInSchema):
    response_code, response_dict = update_object("books_api", "Book", book_id, book)

    return response_code, response_dict


@router.patch(
    "/{int:book_id}", response={200: BookOutSchema, 400: ErrorSchema, 404: ErrorSchema}
)
def patch_book(request: HttpRequest, book_id: int, book: BookInPatchSchema):
    response_code, response_dict = patch_object("books_api", "Book", book_id, book)

    return JsonResponse(status=response_code, data=response_dict)


@router.delete("/{int:book_id}", response={200: None, 404: ErrorSchema})
def delete_book(request: HttpRequest, book_id: int):
    response_code, response_dict = delete_object("books_api", "Book", book_id)
    return JsonResponse(status=response_code, data=response_dict)


@router.get(
    "/{int:book_id}/authors/",
    response={200: list[AuthorOutSubSchema], 404: ErrorSchema},
)
def get_book_authors(request: HttpRequest, book_id: int):
    try:
        authors = Author.objects.prefetch_related("books").filter(books__id=book_id)
    except Author.DoesNotExist:
        return JsonResponse(
            status=404, data={"api_error": f"Requested Author object does not exist"}
        )

    # TODO: Should support pagination in a real-world usage
    return 200, list(authors)


@router.put(
    "/{int:book_id}/authors/",
    response={200: list[AuthorOutSubSchema], 404: ErrorSchema},
)
def update_book_authors(
    request: HttpRequest, book_id: int, authors_list: PrimaryKeyListSchema
):
    new_author_list = Author.objects.filter(id__in=authors_list.ids)
    try:
        target_book = Book.objects.prefetch_related("authors").get(id=book_id)
    except Author.DoesNotExist:
        return JsonResponse(
            status=404, data={"api_error": f"Requested Author object does not exist"}
        )

    target_book.authors.set(new_author_list)

    return 200, list(new_author_list)
