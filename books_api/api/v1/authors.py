from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.helpers import patch_object, delete_object
from books_api.models import Author
from books_api.schemas import (
    AuthorOutSchema,
    ErrorSchema,
    AuthorInSchema,
    AuthorInPatchSchema,
)

router = Router(tags=["Authors"])


@router.get("/", response={200: list[AuthorOutSchema]})
def get_authors(request: HttpRequest):
    authors = Author.objects.all()
    return 200, authors


@router.get("/{int:author_id}", response={200: AuthorOutSchema, 404: ErrorSchema})
def get_author(request: HttpRequest, author_id: int):
    author = get_object_or_404(Author, pk=author_id)
    return author


@router.post("/", response={200: AuthorOutSchema})
def add_author(request: HttpRequest, author: AuthorInSchema):
    # TODO: In production, this should handle possible database-level errors
    # that are raised.
    new_author = Author.objects.create(**author.dict())

    return 200, new_author


@router.put(
    "/{int:author_id}",
    response={200: AuthorOutSchema, 400: ErrorSchema, 404: ErrorSchema},
)
def update_author(request: HttpRequest, author_id: int, author: AuthorInSchema):
    response_code, updated_author = patch_object(
        "books_api", "Author", author_id, author
    )
    return response_code, updated_author


@router.patch(
    "/{int:author_id}",
    response={200: AuthorOutSchema, 400: ErrorSchema, 404: ErrorSchema},
)
def patch_author(request: HttpRequest, author_id: int, author: AuthorInPatchSchema):
    response_code, patched_author = patch_object(
        "books_api", "Author", author_id, author
    )

    return response_code, patched_author


@router.delete("/{int:author_id}", response={200: None, 404: ErrorSchema})
def delete_author(request: HttpRequest, author_id: int):
    response_code, response_dict = delete_object("books_api", "Author", author_id)
    return response_code, response_dict
