import pytest

from datatig.models.field_datetime import FieldDateTimeConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, False, None),
    # none values
    ({"party": None}, False, None),
    # string values
    ({"party": "2025-12-01 19:00:00"}, True, "2025-12-01T19:00:00+00:00"),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldDateTimeConfigModel()
    config._key = "party"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
