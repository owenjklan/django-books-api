from ninja import Schema, ModelSchema

from books_api.models import Book, Publisher


class BookSchema(ModelSchema):
    class Config:
        model = Book
        model_fields = "__all__"


class PublisherSchema(ModelSchema):
    class Config:
        model = Publisher
        model_fields = "__all__"
