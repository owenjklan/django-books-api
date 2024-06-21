from decimal import Decimal

from django.test import TestCase, TransactionTestCase

from books_api.helpers import patch_object
from books_api.models import Publisher, Author, Book
from books_api.schemas import BookInPatchSchema


class ORMHelpersTestCase(TransactionTestCase):
    BOOK_INITIAL_ISBN = "1231234567890"
    BOOK_INITIAL_RRP = Decimal("1.23")
    BOOK_INITIAL_TITLE = "Test Book's Original Title"
    BOOK_INITIAL_FORMAT = "Paperback"

    def setUp(self):
        # Books need publishers
        Publisher.objects.all().delete()
        self.publisher_1 = Publisher.objects.create(name="Test Publisher Number 1")
        self.publisher_2 = Publisher.objects.create(name="Test Publisher Number 2")
        self.author_1 = Author.objects.create(
            first_name="Testy", last_name="Authorson", year_of_birth=1929
        )
        self.author_2 = Author.objects.create(
            first_name="Another", last_name="McAuthor", year_of_birth=1980
        )

        self.book = Book.objects.create(
            title=self.BOOK_INITIAL_TITLE,
            isbn=self.BOOK_INITIAL_ISBN,
            rrp=self.BOOK_INITIAL_RRP,
            format=self.BOOK_INITIAL_FORMAT,
            publisher=self.publisher_1,
        )

    def test_patch_simple_object(self):
        new_title_text = "New Title"
        payload_data = {"title": new_title_text}
        # Patch the title of the book and confirm that Title was the only field that changed
        title_only_payload = BookInPatchSchema(**payload_data)
        status, data = patch_object(
            "books_api", "Book", self.book.id, title_only_payload
        )

        # Confirm successful response code and the title being our new title text
        self.assertEqual(status, 200)
        self.assertEqual(data["title"], new_title_text)

        # Confirm that none of the other fields have changed
        self.assertEqual(data["isbn"], self.BOOK_INITIAL_ISBN)
        self.assertEqual(data["rrp"], self.BOOK_INITIAL_RRP)
        self.assertEqual(data["format"], self.BOOK_INITIAL_FORMAT)
        self.assertEqual(data["publisher"], self.publisher_1.id)

    def test_patch_multiple_fields(self):
        new_title_text = "New Title"
        new_rrp = Decimal("33.33")
        payload_data = {"title": new_title_text, "rrp": new_rrp}

        # Patch the title and RRP of the book and confirm that both fields are
        # the only ones that changed
        title_and_rrp_payload = BookInPatchSchema(**payload_data)
        status, data = patch_object(
            "books_api", "Book", self.book.id, title_and_rrp_payload
        )

        # Confirm successful response code and the title and RRP being updated
        self.assertEqual(status, 200)
        self.assertEqual(data["title"], new_title_text)
        self.assertEqual(data["rrp"], new_rrp)

        # Confirm that none of the other fields have changed
        self.assertEqual(data["isbn"], self.BOOK_INITIAL_ISBN)
        self.assertEqual(data["format"], self.BOOK_INITIAL_FORMAT)
        self.assertEqual(data["publisher"], self.publisher_1.id)

    def test_patch_fk_reference(self):
        new_publisher = Publisher.objects.create(name="Updated Publisher")
        payload_data = {"publisher_id": new_publisher.id}

        # Patch the value of a foreign key field. For our Book class, we're
        # using
        updated_publisher_payload = BookInPatchSchema(**payload_data)
        status, data = patch_object(
            "books_api", "Book", self.book.id, updated_publisher_payload
        )

        # Confirm successful response code and the referenced publisher being updated
        self.assertEqual(status, 200)
        self.assertEqual(data["publisher"], new_publisher.id)

        # Confirm that none of the other fields have changed
        self.assertEqual(data["title"], self.BOOK_INITIAL_TITLE)
        self.assertEqual(data["rrp"], self.BOOK_INITIAL_RRP)
        self.assertEqual(data["isbn"], self.BOOK_INITIAL_ISBN)
        self.assertEqual(data["format"], self.BOOK_INITIAL_FORMAT)

    def test_patch_fk_fails_if_provided_unknown_fk(self):
        new_publisher = Publisher.objects.create(name="Updated Publisher")
        payload_data = {"publisher_id": 10000}

        # Patch the value of a foreign key field. For our Book class, we're
        # using
        updated_publisher_payload = BookInPatchSchema(**payload_data)
        status, data = patch_object(
            "books_api", "Book", self.book.id, updated_publisher_payload
        )

        # Confirm successful response code and the referenced publisher being updated
        self.assertEqual(status, 404)
        self.assertFalse(data["success"])
        self.assertEqual(
            data["message"], "Publisher referenced by 'publisher_id' does not exist"
        )
