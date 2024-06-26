import inspect
import os
import types

from django.test import TestCase

from autodojo.defaults import DefaultErrorResponseSchema
from autodojo.tests.models import DummyModel, RelatedDummyModel
from autodojo.tests.schemas import DummySchema

os.environ["DJANGO_SETTINGS_MODULE"] = "django_books_api.settings"

from django.db import models
from ninja import Schema, ModelSchema

from autodojo.autodojoview import AutoDojoView


# These assume that the Model class used was "Dummy".
# This should affect names of generated response schema
# classes
HTTP_VERB_EXPECTATIONS = {
    "GET": {
        "url_path": "/{int:id}",
        "response_status_codes": {
            200: {
                "annotation": Schema,
                "name": "GeneratedDummyModelOut",
            },
            404: {
                "annotation": Schema,
                "name": "DefaultErrorResponseSchema",
            },
        },
    },
    "GETLIST": {
        "url_path": "/",
        "response_status_codes": {
            200: {
                "annotation": list,
                "name": Schema,
            },
        },
    },
    "POST": {
        "url_path": "/",
        "response_status_codes": {
            200: {
                "annotation": Schema,
                "name": "GeneratedDummyModelOut",
            },
            400: {
                "annotation": Schema,
                "name": "DefaultErrorResponseSchema",
            },
        },
    },
    "PUT": {
        "url_path": "/{int:id}",
        "response_status_codes": {
            200: {
                "annotation": Schema,
                "name": "GeneratedDummyModelOut",
            },
            404: {
                "annotation": Schema,
                "name": "DefaultErrorResponseSchema",
            },
        },
    },
    "PATCH": {
        "url_path": "/{int:id}",
        "response_status_codes": {
            200: {
                "annotation": Schema,
                "name": "GeneratedDummyModelOut",
            },
            404: {
                "annotation": Schema,
                "name": "DefaultErrorResponseSchema",
            },
        },
    },
    "DELETE": {
        "url_path": "/{int:id}",
        "response_status_codes": {
            200: {
                "annotation": None,
            },
            404: {
                "annotation": Schema,
                "name": "DefaultErrorResponseSchema",
            },
        },
    },
}


class TestBasicViewGeneration(TestCase):
    def test_exception_raised_if_schema_and_config_provided(self):
        """
        The AutoDojoView classes are designed to raise an exception if an
        existing Schema class is provided alongside a schema configuration
        dictionary. Purpose being: If the schema is provided, then the
        config dictionary is irrelevant and the opinion here is that the
        user should be aware of this.
        :return:
        """
        ignored_config = {"depth": 2}
        try:
            _ = AutoDojoView(
                DummyModel,
                "GET",
                request_schema=DummySchema,
                request_schema_config=ignored_config,
            )
        except ValueError as e:
            self.assertEqual(
                str(e),
                "Supplied request_schema_config will be ignored because request_schema class was supplied",
            )

        # Let's do it again, but for the response schema/schema_config
        try:
            _ = AutoDojoView(
                DummyModel,
                "GET",
                response_schema=DummySchema,
                response_schema_config=ignored_config,
            )
        except ValueError as e:
            self.assertEqual(
                str(e),
                "Supplied response_schema_config will be ignored because response_schema class was supplied",
            )

    def test_basic_view_generation_for_methods(self):
        """
        For each of the verbs that we have generator classes for,
        test the basic view generation.

        By "basic", we mean:
        - No schema config parameters, other than those defined as
          defaults inside the Verb-specific subclass of AutoDojoViewGenerator
        """
        for http_verb, expectations in HTTP_VERB_EXPECTATIONS.items():
            print(f"\n--[[ Testing basic view generation for verb: {http_verb} ]]--")
            auto_view = AutoDojoView(DummyModel, http_verb)

            self.assertEqual(auto_view.url_path, expectations["url_path"])
            print(f"  - Expected URL path matched {expectations['url_path']}")

            # Inspect the response dictionary that was generated
            response_dict = auto_view.response_config
            print("  --[[ Inspecting generated view response dict... ]]--")
            # Confirm expected number of status-codes in returned response dict
            self.assertEqual(
                len(response_dict.keys()),
                len(expectations["response_status_codes"].keys()),
            )

            for status_code, status_expectations in expectations[
                "response_status_codes"
            ].items():
                # Is the expected status code defined in the returned response dict?
                print(f"    - Status code: {status_code}")
                self.assertTrue(status_code in response_dict.keys())

                #
                expected_type = status_expectations["annotation"]
                if expected_type == None:
                    self.assertEqual(response_dict[status_code], None)
                elif expected_type not in [list, dict, tuple]:
                    # Class types
                    self.assertTrue(
                        issubclass(response_dict[status_code], expected_type)
                    )
                    # For class-based expected response types, check the name
                    if "name" in status_expectations:
                        self.assertEqual(
                            response_dict[status_code].__name__,
                            status_expectations["name"],
                        )
                else:
                    # TODO: Work out how to inspect the type the list contains
                    # types.GenericAlias was introduced in 3.9
                    # https://docs.python.org/3/library/stdtypes.html#types-genericalias
                    self.assertEqual(
                        response_dict[status_code],
                        types.GenericAlias(expected_type, auto_view.response_schema),
                    )
            print(f"--[[ End of {http_verb}-specific test ]]--")
