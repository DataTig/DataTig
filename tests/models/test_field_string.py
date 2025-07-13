import pytest

from datatig.models.field_string import FieldStringConfigModel
from datatig.models.record import RecordModel

test_get_urls_in_value_data = [
    ({}, []),
    ({"description": None}, []),
    (
        {"description": "Find out more at https://www.datatig.com/"},
        ["https://www.datatig.com/"],
    ),
    ({"description": "https://www.datatig.com/"}, ["https://www.datatig.com/"]),
    (
        {"description": "https://www.datatig.com/ to find out more"},
        ["https://www.datatig.com/"],
    ),
    (
        {
            "description": '<a href="https://www.datatig.com/">Visit to find out more</a>'
        },
        [],
    ),
]


@pytest.mark.parametrize("data, expected_value", test_get_urls_in_value_data)
def test_get_urls_in_value(data, expected_value):
    config = FieldStringConfigModel()
    config._key = "description"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert expected_value == value.get_urls_in_value()


test_set_value_data = [
    ({}, False, None),
    # none values
    ({"cat": None}, False, None),
    # values
    ({"cat": "floffy"}, True, "floffy"),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldStringConfigModel()
    config._key = "cat"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
