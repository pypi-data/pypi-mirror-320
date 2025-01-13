import unittest
from datetime import date, datetime
from enum import Enum

from src.flask_inputfilter.Filter import (
    ArrayExplodeFilter,
    RemoveEmojisFilter,
    SlugifyFilter,
    StringTrimFilter,
    ToAlphaNumericFilter,
    ToBooleanFilter,
    ToCamelCaseFilter,
    ToDateFilter,
    ToDateTimeFilter,
    ToEnumFilter,
    ToFloatFilter,
    ToIntegerFilter,
    ToIsoFilter,
    ToLowerFilter,
    ToNormalizedUnicodeFilter,
    ToNullFilter,
    ToPascaleCaseFilter,
    ToSnakeCaseFilter,
    ToStringFilter,
    ToUpperFilter,
    TruncateFilter,
    WhitespaceCollapseFilter,
)
from src.flask_inputfilter.InputFilter import InputFilter


class TestInputFilter(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up a InputFilter instance for testing.
        """

        self.inputFilter = InputFilter()

    def test_array_explode_filter(self) -> None:
        """
        Test that ArrayExplodeFilter explodes a string to a list.
        """

        self.inputFilter.add(
            "tags",
            required=False,
            filters=[ArrayExplodeFilter()],
        )

        validated_data = self.inputFilter.validateData(
            {"tags": "tag1,tag2,tag3"}
        )

        self.assertEqual(validated_data["tags"], ["tag1", "tag2", "tag3"])

        self.inputFilter.add(
            "items", required=False, filters=[ArrayExplodeFilter(";")]
        )

        validated_data = self.inputFilter.validateData(
            {"items": "item1;item2;item3"}
        )

        self.assertEqual(validated_data["items"], ["item1", "item2", "item3"])

    def test_remove_emojis_filter(self) -> None:
        """
        Test that RemoveEmojisFilter removes emojis from a string.
        """

        self.inputFilter.add(
            "text",
            required=False,
            filters=[RemoveEmojisFilter()],
        )

        validated_data = self.inputFilter.validateData(
            {"text": "Hello World! 😊"}
        )

        self.assertEqual(validated_data["text"], "Hello World! ")

    def test_slugify_filter(self) -> None:
        """
        Test that SlugifyFilter slugifies a string.
        """

        self.inputFilter.add(
            "slug",
            required=False,
            filters=[SlugifyFilter()],
        )

        validated_data = self.inputFilter.validateData(
            {"slug": "Hello World!"}
        )

        self.assertEqual(validated_data["slug"], "hello-world")

    def test_string_trim_filter(self) -> None:
        """
        Test that StringTrimFilter trims whitespace.
        """

        self.inputFilter.add(
            "trimmed_field", required=False, filters=[StringTrimFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"trimmed_field": "   Hello World   "}
        )

        self.assertEqual(validated_data["trimmed_field"], "Hello World")

    def test_to_alphanumeric_filter(self) -> None:
        """
        Test that ToAlphaNumericFilter removes non-alphanumeric characters.
        """

        self.inputFilter.add(
            "alphanumeric_field",
            required=False,
            filters=[ToAlphaNumericFilter()],
        )

        validated_data = self.inputFilter.validateData(
            {"alphanumeric_field": "Hello World!123"}
        )

        self.assertEqual(validated_data["alphanumeric_field"], "HelloWorld123")

    def test_to_bool_filter(self) -> None:
        """
        Test that ToBooleanFilter converts string to boolean.
        """

        self.inputFilter.add(
            "is_active", required=True, filters=[ToBooleanFilter()]
        )

        validated_data = self.inputFilter.validateData({"is_active": "true"})

        self.assertTrue(validated_data["is_active"])

    def test_to_camel_case_filter(self) -> None:
        """
        Test that CamelCaseFilter converts string to camel case.
        """

        self.inputFilter.add(
            "username", required=True, filters=[ToCamelCaseFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"username": "test user"}
        )

        self.assertEqual(validated_data["username"], "testUser")

    def test_to_date_filter(self) -> None:
        """
        Test that ToDateFilter converts string to date.
        """

        self.inputFilter.add("dob", required=True, filters=[ToDateFilter()])

        validated_data = self.inputFilter.validateData({"dob": "1996-12-01"})

        self.assertEqual(validated_data["dob"], date(1996, 12, 1))

    def test_to_datetime_filter(self) -> None:
        """
        Test that ToDateTimeFilter converts string to datetime.
        """

        self.inputFilter.add(
            "created_at", required=True, filters=[ToDateTimeFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"created_at": "2021-01-01T12:00:00"}
        )

        self.assertEqual(
            validated_data["created_at"],
            datetime(2021, 1, 1, 12, 0, 0),
        )

    def test_to_enum_filter(self) -> None:
        """
        Test that EnumFilter validates a string against a list of values.
        """

        class ColorEnum(Enum):
            RED = "red"
            GREEN = "green"
            BLUE = "blue"

        self.inputFilter.add(
            "color",
            required=True,
            filters=[ToEnumFilter(ColorEnum)],
        )

        validated_data = self.inputFilter.validateData({"color": "red"})

        self.assertEqual(validated_data["color"], ColorEnum.RED)

    def test_to_float_filter(self) -> None:
        """
        Test that ToFloatFilter converts string to float.
        """

        self.inputFilter.add("price", required=True, filters=[ToFloatFilter()])

        validated_data = self.inputFilter.validateData({"price": "19.99"})

        self.assertEqual(validated_data["price"], 19.99)

    def test_to_integer_filter(self) -> None:
        """
        Test that ToIntegerFilter converts string to integer.
        """

        self.inputFilter.add("age", required=True, filters=[ToIntegerFilter()])

        validated_data = self.inputFilter.validateData({"age": "25"})

        self.assertEqual(validated_data["age"], 25)

    def test_to_iso_filter(self) -> None:
        """
        Test that ToIsoFilter converts date or datetime to
        ISO 8601 formatted string.
        """

        self.inputFilter.add("date", filters=[ToIsoFilter()])

        validated_data = self.inputFilter.validateData(
            {"date": date(2021, 1, 1)}
        )

        self.assertEqual(validated_data["date"], "2021-01-01")

        self.inputFilter.add("datetime", filters=[ToIsoFilter()])

        validated_data = self.inputFilter.validateData(
            {"datetime": datetime(2021, 1, 1, 12, 0, 0)}
        )

        self.assertEqual(validated_data["datetime"], "2021-01-01T12:00:00")

    def test_to_lower_filter(self) -> None:
        """
        Test that ToLowerFilter converts string to lowercase.
        """

        self.inputFilter.add(
            "username", required=True, filters=[ToLowerFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"username": "TESTUSER"}
        )

        self.assertEqual(validated_data["username"], "testuser")

    def test_to_normalized_unicode_filter(self) -> None:
        """
        Test that NormalizeUnicodeFilter normalizes Unicode characters.
        """

        self.inputFilter.add(
            "unicode_field",
            required=False,
            filters=[ToNormalizedUnicodeFilter()],
        )

        validated_data = self.inputFilter.validateData(
            {"unicode_field": "Héllô Wôrld"}
        )

        self.assertEqual(validated_data["unicode_field"], "Hello World")

    def test_to_null_filter(self) -> None:
        """
        Test that ToNullFilter transforms empty string to None.
        """

        self.inputFilter.add(
            "optional_field", required=False, filters=[ToNullFilter()]
        )

        validated_data = self.inputFilter.validateData({"optional_field": ""})

        self.assertIsNone(validated_data["optional_field"])

    def test_to_pascal_case_filter(self) -> None:
        """
        Test that PascalCaseFilter converts string to pascal case.
        """

        self.inputFilter.add(
            "username", required=True, filters=[ToPascaleCaseFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"username": "test user"}
        )

        self.assertEqual(validated_data["username"], "TestUser")

    def test_snake_case_filter(self) -> None:
        """
        Test that SnakeCaseFilter converts string to snake case.
        """

        self.inputFilter.add(
            "username", required=True, filters=[ToSnakeCaseFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"username": "TestUser"}
        )

        self.assertEqual(validated_data["username"], "test_user")

    def test_to_string_filter(self) -> None:
        """
        Test that ToStringFilter converts any type to string.
        """

        self.inputFilter.add("age", required=True, filters=[ToStringFilter()])

        validated_data = self.inputFilter.validateData({"age": 25})

        self.assertEqual(validated_data["age"], "25")

    def test_to_upper_filter(self) -> None:
        """
        Test that ToUpperFilter converts string to uppercase.
        """

        self.inputFilter.add(
            "username", required=True, filters=[ToUpperFilter()]
        )

        validated_data = self.inputFilter.validateData(
            {"username": "testuser"}
        )

        self.assertEqual(validated_data["username"], "TESTUSER")

    def test_truncate_filter(self) -> None:
        """
        Test that TruncateFilter truncates a string.
        """

        self.inputFilter.add(
            "truncated_field", required=False, filters=[TruncateFilter(5)]
        )

        validated_data = self.inputFilter.validateData(
            {"truncated_field": "Hello World"}
        )

        self.assertEqual(validated_data["truncated_field"], "Hello")

    def test_whitespace_collapse_filter(self) -> None:
        """
        Test that WhitespaceCollapseFilter collapses whitespace.
        """

        self.inputFilter.add(
            "collapsed_field",
            required=False,
            filters=[WhitespaceCollapseFilter()],
        )

        validated_data = self.inputFilter.validateData(
            {"collapsed_field": "Hello    World"}
        )

        self.assertEqual(validated_data["collapsed_field"], "Hello World")


if __name__ == "__main__":
    unittest.main()
