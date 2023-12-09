import datetime
from unittest import TestCase

from apptk import coerce


class ToDatetimeTestCase(TestCase):
    def test_integer(self):
        actual = coerce.to_datetime(123)
        expected = datetime.datetime.utcfromtimestamp(123)
        self.assertEqual(actual, expected)

    def test_float(self):
        actual = coerce.to_datetime(float(123))
        expected = datetime.datetime.utcfromtimestamp(123)
        self.assertEqual(actual, expected)

    def test_date(self):
        actual = coerce.to_datetime(datetime.date(2006, 1, 1))
        expected = datetime.datetime(2006, 1, 1)
        self.assertEqual(actual, expected)

    def test_datetime(self):
        input = datetime.datetime(2006, 1, 1)
        actual = coerce.to_datetime(input)
        expected = datetime.datetime(2006, 1, 1)
        self.assertEqual(actual, expected)
        self.assertIs(actual, input)

    def test_string(self):
        input = "2006-01-01"
        actual = coerce.to_datetime(input)
        expected = datetime.datetime(2006, 1, 1)
        self.assertEqual(actual, expected)

    def test_string_with_time(self):
        input = "2006-01-01T09:41:13"
        actual = coerce.to_datetime(input)
        expected = datetime.datetime(2006, 1, 1, 9, 41, 13)
        self.assertEqual(actual, expected)
