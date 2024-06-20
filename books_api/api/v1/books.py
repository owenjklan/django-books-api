from django.db.models.fields.related import ForeignKey
from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

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
    patched_book = get_object_or_404(Book, pk=book_id)
    patch_fields = book.dict(exclude_unset=True)

    for attr, value in patch_fields.items():
        # Determine if the supplied attribute is a foreign key or not
        # Check for a field of the supplied attribute name
        field_meta = Book._meta.get_field(attr)

        if field_meta.__class__ is ForeignKey:
            print(f"Foreign key attribute found: {attr}. Value: {value}")
            referenced_model = get_object_or_404(field_meta.related_model, pk=value)
            setattr(patched_book, attr, referenced_model)
        else:
            setattr(patched_book, attr, value)

    patched_book.save()

    return patched_book


@router.delete("/{int:book_id}")
def delete_book(request: HttpRequest, book_id: int) -> JsonResponse:
    return JsonResponse({"book_id": 1})
