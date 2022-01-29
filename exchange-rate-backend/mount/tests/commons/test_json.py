import datetime
from decimal import Decimal
import pytest

from app.commons.json import dumps, loads


def test_dumps_valid():
    data = {
        "name": "First Last",
        "age": 50,
        "weight": Decimal("175.514159265358979323"),
        "dob": datetime.datetime(1960, 7, 8, 9, 10, 11),
    }

    expected = (
        '{"name":"First Last",'
        '"age":50,'
        '"weight":175.514159265358979323,'
        '"dob":"1960-07-08T09:10:11+00:00"}'
    )

    assert dumps(data) == expected


def test_dumps_string():
    assert dumps("ABC") == '"ABC"'


def test_dumps_int():
    assert dumps(99) == "99"


def test_loads_valid():
    expected = {
        "name": "First Last",
        "age": 50,
        "weight": 175.514159265358979323,
        "dob": "1960-07-08T09:10:11+00:00",
    }

    data = (
        '{"name":"First Last",'
        '"age":50,'
        '"weight":175.514159265358979323,'
        '"dob":"1960-07-08T09:10:11+00:00"}'
    )

    assert loads(data) == expected


def test_loads_invalid():
    data = (
        '{"name:"First Last",'
        '"age":50,'
        '"weight":175.514159265358979323,'
        '"dob":"1960-07-08T09:10:11+00:00"}'
    )
    with pytest.raises(Exception):
        loads(data)
