import pytest

from datatig.models.field_boolean import FieldBooleanConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, False, None),
    # none values
    ({"has_cat": None}, False, None),
    # true values
    ({"has_cat": True}, True, True),
    ({"has_cat": "True"}, True, True),
    ({"has_cat": "true"}, True, True),
    ({"has_cat": "   True"}, True, True),
    ({"has_cat": "    true"}, True, True),
    ({"has_cat": "1"}, True, True),
    ({"has_cat": "      1"}, True, True),
    ({"has_cat": 1}, True, True),
    # false values
    ({"has_cat": False}, True, False),
    ({"has_cat": "False"}, True, False),
    ({"has_cat": "false"}, True, False),
    ({"has_cat": "   False"}, True, False),
    ({"has_cat": "    false"}, True, False),
    ({"has_cat": "0"}, True, False),
    ({"has_cat": "      0"}, True, False),
    ({"has_cat": 0}, True, False),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldBooleanConfigModel()
    config._key = "has_cat"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
