from ninja import Schema, ModelSchema

from books_api.models import Book, Publisher, Author


class BookSchema(ModelSchema):
    publisher: "PublisherSchema"
    authors: list["AuthorSubSchema"]

    class Config:
        model = Book
        model_fields = "__all__"


class BookSubSchema(ModelSchema):
    class Config:
        model = Book
        model_fields = "__all__"


class PublisherSchema(ModelSchema):
    class Config:
        model = Publisher
        model_fields = "__all__"


class AuthorSchema(ModelSchema):
    """
    This schema is used when the Author object is the main
    object being queried
    """

    books: list["BookSubSchema"]

    class Config:
        model = Author
        model_fields = "__all__"


class AuthorSubSchema(ModelSchema):
    """
    This schema is used when Author information is provided
    as additional, related information for a parent object's
    Schema. For example, when authors are returned as part
    of a book's detail, we don't need "books" listed again
    as part of the "authors" key.
    """

    class Config:
        model = Author
        model_fields = "__all__"
        model_exclude = ["books"]
