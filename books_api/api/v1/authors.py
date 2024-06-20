from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.models import Author
from books_api.schemas import AuthorOutSchema

router = Router(tags=["Authors"])


@router.get("/", response=list[AuthorOutSchema])
def get_authors(request: HttpRequest) -> JsonResponse:
    authors = Author.objects.all()
    return authors


@router.get("/{int:author_id}", response=AuthorOutSchema)
def get_author(request: HttpRequest, author_id: int) -> JsonResponse:
    author = get_object_or_404(Author, pk=author_id)
    return author
