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


@router.get("/", response=list[AuthorOutSchema])
def get_authors(request: HttpRequest) -> JsonResponse:
    authors = Author.objects.all()
    return authors


@router.get("/{int:author_id}", response=AuthorOutSchema)
def get_author(request: HttpRequest, author_id: int) -> JsonResponse:
    author = get_object_or_404(Author, pk=author_id)
    return author


@router.post("/", response={200: AuthorOutSchema, 400: ErrorSchema, 404: ErrorSchema})
def add_author(request: HttpRequest, author: AuthorInSchema) -> JsonResponse:
    new_author = Author.objects.create(**author.dict())

    return new_author


@router.put(
    "/{int:author_id}",
    response={200: AuthorOutSchema, 400: ErrorSchema, 404: ErrorSchema},
)
def update_author(
    request: HttpRequest, author_id: int, author: AuthorInSchema
) -> JsonResponse:
    updated_author = Author.objects.update(pk=author_id, **author.dict())
    return updated_author


@router.patch(
    "/{int:author_id}",
    response={200: AuthorOutSchema, 400: ErrorSchema, 404: ErrorSchema},
)
def patch_author(
    request: HttpRequest, author_id: int, author: AuthorInPatchSchema
) -> JsonResponse:
    response_code, response_dict = patch_object(
        "books_api", "Author", author_id, author
    )

    return JsonResponse(status=response_code, data=response_dict)


@router.delete("/{int:author_id}", response={200: None, 404: ErrorSchema})
def delete_author(request: HttpRequest, author_id: int) -> JsonResponse:
    response_code, response_dict = delete_object("books_api", "Author", author_id)
    return JsonResponse(status=response_code, data=response_dict)
