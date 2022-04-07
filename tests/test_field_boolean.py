import pytest

from datatig.models.field_boolean import FieldBooleanConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, None),
    # none values
    ({"has_cat": None}, None),
    # true values
    ({"has_cat": True}, True),
    ({"has_cat": "True"}, True),
    ({"has_cat": "true"}, True),
    ({"has_cat": "   True"}, True),
    ({"has_cat": "    true"}, True),
    ({"has_cat": "1"}, True),
    ({"has_cat": "      1"}, True),
    ({"has_cat": 1}, True),
    # false values
    ({"has_cat": False}, False),
    ({"has_cat": "False"}, False),
    ({"has_cat": "false"}, False),
    ({"has_cat": "   False"}, False),
    ({"has_cat": "    false"}, False),
    ({"has_cat": "0"}, False),
    ({"has_cat": "      0"}, False),
    ({"has_cat": 0}, False),
]


@pytest.mark.parametrize("data, expected_value", test_set_value_data)
def test_set_value(data, expected_value):
    config = FieldBooleanConfigModel()
    config._key = "has_cat"
    record = RecordModel()
    record._data = data
    value = config.get_value_object_from_record(record)
    assert expected_value == value.get_value()
