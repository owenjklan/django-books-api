from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from books_api.models import Publisher
from books_api.schemas import PublisherOutSchema

router = Router(tags=["Publishers"])


@router.get("/", response=list[PublisherOutSchema])
def get_publishers(request: HttpRequest) -> JsonResponse:
    publishers = Publisher.objects.all()
    return publishers


@router.get("/{int:publisher_id}", response=PublisherOutSchema)
def get_publisher(request: HttpRequest, publisher_id: int) -> JsonResponse:
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return publisher
