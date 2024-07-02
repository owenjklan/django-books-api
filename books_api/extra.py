"""
This example is to demonstrate how views/routes that were
not created by AutoDojo can be included in a Ninja API
"""

from django.http import HttpRequest
from ninja import Router

from books_api.models import Book

router = Router(tags=["Book"])


@router.get("/{int:id}/authors", response={200: list[int]})
def get_book_authors(request: HttpRequest, id: int):
    authors = Book.objects.get(pk=id).authors.all()
    author_ids = authors.values("id")
    return list[authors.values("id")]
