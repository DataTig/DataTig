import pytest

from datatig.models.field_list_dictionaries import FieldListDictionariesConfigModel
from datatig.models.record import RecordModel

test_different_to_data = [
    ({"l": []}, {"l": []}, False),
    ({"l": [{"title": "cats"}]}, {"l": []}, True),
    ({"l": [{"title": "cats"}]}, {"l": [{"title": "cats"}]}, False),
    ({"l": [{"title": "cats"}]}, {"l": [{"title": "dogs"}]}, True),
]


@pytest.mark.parametrize("data1, data2, expected_result", test_different_to_data)
def test_different_to(data1, data2, expected_result):
    record = None
    field = FieldListDictionariesConfigModel()
    field.load({"id": "l", "key": "l", "fields": [{"id": "title", "key": "title"}]})
    v1 = field.get_value_object(record, data1)
    v2 = field.get_value_object(record, data2)
    assert expected_result == v1.different_to(v2)


test_set_value_data = [
    ({}, False, ""),
    # none values
    ({"l": None}, False, ""),
    # values
    ({"l": [{"title": "Bob"}]}, True, "List of 1 dictionary"),
]


@pytest.mark.parametrize("data, has_value, expected_value", test_set_value_data)
def test_set_value(data, has_value, expected_value):
    config = FieldListDictionariesConfigModel()
    config.load({"id": "l", "key": "l", "fields": [{"id": "title", "key": "title"}]})
    record = RecordModel()
    record._data = data
    value = config.get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
