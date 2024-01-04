import datetime

from bug_trail_core.sqlite3_utils import serialize_to_sqlite_supported


def test_serialize_to_sqlite_supported_none():
    assert serialize_to_sqlite_supported(None) is None


def test_serialize_to_sqlite_supported_primitive():
    assert serialize_to_sqlite_supported(1) == 1
    assert serialize_to_sqlite_supported(1.0) == 1.0
    assert serialize_to_sqlite_supported("test") == "test"
    assert serialize_to_sqlite_supported(b"bytes") == b"bytes"


def test_serialize_to_sqlite_supported_datetime():
    date = datetime.date.today()
    time = datetime.datetime.now()
    assert serialize_to_sqlite_supported(date) == date
    assert serialize_to_sqlite_supported(time) == time


def test_serialize_to_sqlite_supported_other():
    class CustomObject:
        def __str__(self):
            return "custom_object"

    custom_obj = CustomObject()
    assert serialize_to_sqlite_supported(custom_obj) == "custom_object"
    assert serialize_to_sqlite_supported([1, 2, 3]) == "[1, 2, 3]"
