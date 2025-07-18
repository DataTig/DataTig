import pytest

from datatig.models.field_timezone import FieldTimeZoneConfigModel
from datatig.models.record import RecordModel

test_set_value_data = [
    ({}, False, None),
    # none values
    ({"tz": None}, False, None),
    # good values
    ({"tz": "Europe/London"}, True, "Europe/London"),
    # bad values
    ({"tz": "Europe/Chicago"}, True, "UTC"),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldTimeZoneConfigModel()
    config._key = "tz"
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
