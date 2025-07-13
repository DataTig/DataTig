import pytest

from datatig.models.field_markdown import FieldMarkdownConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, False, None),
    # none values
    ({"cat": None}, False, None),
    # values
    ({"cat": "so **floffy**"}, True, "so **floffy**"),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldMarkdownConfigModel()
    config._key = "cat"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
