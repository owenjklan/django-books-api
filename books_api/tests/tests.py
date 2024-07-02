from decimal import Decimal

from django.test import TransactionTestCase, Client

from books_api.helpers import patch_object
from books_api.models import Publisher, Author, Book
from books_api.schemas import BookInPatchSchema

BOOK_INITIAL_ISBN = "1231234567890"
BOOK_INITIAL_RRP = Decimal("1.23")
BOOK_INITIAL_TITLE = "Test Book's Original Title"
BOOK_INITIAL_FORMAT = "Paperback"


class ORMHelpersTestCase(TransactionTestCase):
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
            title=BOOK_INITIAL_TITLE,
            isbn=BOOK_INITIAL_ISBN,
            rrp=BOOK_INITIAL_RRP,
            format=BOOK_INITIAL_FORMAT,
            publisher=self.publisher_1,
        )

    def test_patch_simple_object(self):
        new_title_text = "New Title"
        payload_data = {"title": new_title_text}
        # Patch the title of the book and confirm that Title was the only field that changed
        title_only_payload = BookInPatchSchema(**payload_data)
        status, patched_object = patch_object(
            "books_api", "Book", self.book.id, title_only_payload
        )

        # Confirm successful response code and the title being our new title text
        self.assertEqual(status, 200)
        self.assertEqual(patched_object.title, new_title_text)

        # Confirm that none of the other fields have changed
        self.assertEqual(patched_object.isbn, BOOK_INITIAL_ISBN)
        self.assertEqual(patched_object.rrp, BOOK_INITIAL_RRP)
        self.assertEqual(patched_object.format, BOOK_INITIAL_FORMAT)
        self.assertEqual(patched_object.publisher, self.publisher_1)

    def test_patch_multiple_fields(self):
        new_title_text = "New Title"
        new_rrp = Decimal("33.33")
        payload_data = {"title": new_title_text, "rrp": new_rrp}

        # Patch the title and RRP of the book and confirm that both fields are
        # the only ones that changed
        title_and_rrp_payload = BookInPatchSchema(**payload_data)
        status, patched_object = patch_object(
            "books_api", "Book", self.book.id, title_and_rrp_payload
        )

        # Confirm successful response code and the title and RRP being updated
        self.assertEqual(status, 200)
        self.assertEqual(patched_object.title, new_title_text)
        self.assertEqual(patched_object.rrp, new_rrp)

        # Confirm that none of the other fields have changed
        self.assertEqual(patched_object.isbn, BOOK_INITIAL_ISBN)
        self.assertEqual(patched_object.format, BOOK_INITIAL_FORMAT)
        self.assertEqual(patched_object.publisher, self.publisher_1)

    def test_patch_fk_reference(self):
        new_publisher = Publisher.objects.create(name="Updated Publisher")
        payload_data = {"publisher_id": new_publisher.id}

        # Patch the value of a foreign key field. For our Book class, we're
        # using
        updated_publisher_payload = BookInPatchSchema(**payload_data)
        status, patched_object = patch_object(
            "books_api", "Book", self.book.id, updated_publisher_payload
        )

        # Confirm successful response code and the referenced publisher being updated
        self.assertEqual(status, 200)
        self.assertEqual(patched_object.publisher, new_publisher)

        # Confirm that none of the other fields have changed
        self.assertEqual(patched_object.title, BOOK_INITIAL_TITLE)
        self.assertEqual(patched_object.rrp, BOOK_INITIAL_RRP)
        self.assertEqual(patched_object.isbn, BOOK_INITIAL_ISBN)
        self.assertEqual(patched_object.format, BOOK_INITIAL_FORMAT)

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
        self.assertEqual(
            data["api_error"], "Publisher referenced by 'publisher_id' does not exist"
        )


class APIClientTests(TransactionTestCase):
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
            title=BOOK_INITIAL_TITLE,
            isbn=BOOK_INITIAL_ISBN,
            rrp=BOOK_INITIAL_RRP,
            format=BOOK_INITIAL_FORMAT,
            publisher=self.publisher_1,
        )

    def test_update_book_via_http(self):
        """
        This test method is essentially superfluous, but present to demonstrate the use
        of Django's Test HTTP client in a fairly simple case.
        """
        client = Client()

        # For PUT-based updates, we need to provide all required fields
        book_update_payload = self.book.__dict__
        # Pop the '_state' key, because it will upset the JSON serialisation
        _ = book_update_payload.pop("_state", None)

        # Change the Title
        book_update_payload["title"] = "PUT-updated title"

        response = client.put(
            f"/api/books/{self.book.id}",
            book_update_payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(
            response_json["title"],
            "PUT-updated title",
        )
