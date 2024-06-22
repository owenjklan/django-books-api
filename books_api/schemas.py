from typing import Literal

from ninja import Schema, ModelSchema

from books_api.models import Book, Publisher, Author, Category


class ErrorSchema(Schema):
    api_error: str


class BookOutSchema(ModelSchema):
    publisher: "PublisherOutSchema"
    authors: list["AuthorOutSubSchema"]

    class Config:
        model = Book
        model_fields = "__all__"


class BookInSchema(ModelSchema):
    class Config:
        model = Book
        model_exclude = ["id"]  # ID provided in URL


class BookInPatchSchema(ModelSchema):
    class Meta:
        model = Book
        fields = "__all__"
        exclude = ("id",)
        fields_optional = "__all__"


class BookOutSubSchema(ModelSchema):
    class Config:
        model = Book
        model_fields = "__all__"


class PublisherOutSchema(ModelSchema):
    class Config:
        model = Publisher
        model_fields = "__all__"


class CategoryOutSchema(ModelSchema):
    class Config:
        model = Category
        model_fields = "__all__"


class AuthorInSchema(ModelSchema):
    class Config:
        model = Author
        model_exclude = ["id", "books"]  # ID provided in URL


class AuthorInPatchSchema(ModelSchema):
    class Meta:
        model = Author
        fields = "__all__"
        exclude = (
            "id",
            "books",
        )
        fields_optional = "__all__"


#
# class BookAuthorListSchema(ModelSchema):
#     class Meta:
#         model = Author
#         fields = "__all__"
#         exclude = ("id", "books")


class AuthorOutSchema(ModelSchema):
    """
    This schema is used when the Author object is the main
    object being queried
    """

    class Config:
        model = Author
        model_fields = "__all__"


class AuthorOutSubSchema(ModelSchema):
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


class PrimaryKeyListSchema(Schema):
    ids: list[int]
