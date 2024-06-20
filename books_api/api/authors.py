from django.http import JsonResponse, HttpRequest
from ninja import Router

from ..models import Author
from ..schemas import AuthorSchema

router = Router(tags=["Authors"])


@router.get("/", response=list[AuthorSchema])
def get_authors(request: HttpRequest) -> JsonResponse:
    authors = Author.objects.all()
    return authors


@router.get("/{int:author_id}", response=AuthorSchema)
def get_author(request: HttpRequest, author_id: int) -> JsonResponse:
    author = Author.objects.get(pk=author_id)
    return author
