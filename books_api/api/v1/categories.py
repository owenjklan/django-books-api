from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.models import Category
from books_api.schemas import CategoryOutSchema

router = Router(tags=["Categories"])


@router.get("/", response=list[CategoryOutSchema])
def get_categories(request: HttpRequest) -> JsonResponse:
    categories = Category.objects.all()
    return categories


@router.get("/{int:category_id}", response=CategoryOutSchema)
def get_category(request: HttpRequest, category_id: int) -> JsonResponse:
    category = get_object_or_404(Category, pk=category_id)
    return category
