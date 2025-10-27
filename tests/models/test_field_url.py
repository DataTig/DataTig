import tempfile

import pytest

from datatig.models.record import RecordModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.validate.jsonschema import _json_schema_validator

test_set_value_data = [
    # missing key when not required
    (False, {}, False, None, False),
    # missing key when required
    (True, {}, False, None, True),
    # no value when not required
    (False, {"web": ""}, False, "", False),
    # no value when required
    (True, {"web": ""}, False, "", True),
    # values
    (
        True,
        {"web": "https://www.datatig.com/"},
        True,
        "https://www.datatig.com/",
        False,
    ),
    (
        True,
        {"web": "https://www.datatig.com"},
        True,
        "https://www.datatig.com",
        False,
    ),
    (
        True,
        {"web": "ftp://www.datatig.com"},
        True,
        "ftp://www.datatig.com",
        True,
    ),
    (
        True,
        {"web": "https://www.datatig.com is the correct URL"},
        True,
        "https://www.datatig.com is the correct URL",
        True,
    ),
    (
        True,
        {"web": "search for datatig"},
        True,
        "search for datatig",
        True,
    ),
    # bad values
    (False, {"web": None}, False, None, True),
]


@pytest.mark.parametrize(
    "required, data, has_value, expected_value, expected_to_error", test_set_value_data
)
def test_set_value(required, data, has_value, expected_value, expected_to_error):
    site_config = SiteConfigModel(tempfile.gettempdir())
    type = TypeModel(site_config)
    type.load_from_config(
        {"fields": [{"type": "url", "id": "web", "required": required}]}
    )
    record = RecordModel()
    record._data = data
    value = type.get_field("web").get_value_object(record, data)
    assert has_value == value.has_value()
    assert expected_value == value.get_value()
    schema_validator = _json_schema_validator(type)
    actual_errors = sorted(schema_validator.iter_errors(data), key=str)
    if expected_to_error:
        assert len(actual_errors) >= 1
    else:
        assert len(actual_errors) == 0
