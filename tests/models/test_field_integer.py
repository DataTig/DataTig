import pytest

from datatig.models.field_integer import FieldIntegerConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, False, None),
    # none values
    ({"party_attendence": None}, False, None),
    # string values
    ({"party_attendence": "123"}, True, 123),
    # integer values
    ({"party_attendence": 123}, True, 123),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldIntegerConfigModel()
    config._key = "party_attendence"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
