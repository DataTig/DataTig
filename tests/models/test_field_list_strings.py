import pytest

from datatig.models.field_list_strings import FieldListStringsConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, False, []),
    # none values
    ({"party_attendence": None}, False, []),
    # values
    ({"party_attendence": ["Alice", "Bob", "Eve"]}, True, ["Alice", "Bob", "Eve"]),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldListStringsConfigModel()
    config._key = "party_attendence"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
