import pytest

from datatig.exceptions import SiteConfigurationException
from datatig.models.field_enum import FieldEnumConfigModel

test_good_config_data = [
    (
        {"id": "f", "choices": ["cat", "dog"]},
        {
            "choices": [
                {"value": "cat", "title": "cat"},
                {"value": "dog", "title": "dog"},
            ]
        },
    ),
    (
        {"id": "f", "choices": [{"value": "cat"}, "dog"]},
        {
            "choices": [
                {"value": "cat", "title": "cat"},
                {"value": "dog", "title": "dog"},
            ]
        },
    ),
    (
        {"id": "f", "choices": [{"value": "cat", "title": "Cat"}, "dog"]},
        {
            "choices": [
                {"value": "cat", "title": "Cat"},
                {"value": "dog", "title": "dog"},
            ]
        },
    ),
]


@pytest.mark.parametrize("field_config, expected_extra_config", test_good_config_data)
def test_good_config(field_config, expected_extra_config):
    config = FieldEnumConfigModel()
    config.load(field_config)
    assert expected_extra_config == config.get_extra_config()


test_bad_config_data = [
    (
        {"id": "f"},
        "No choices specified",
    ),
    (
        {"id": "f", "choices": [{}]},
        "No key in choice",
    ),
    (
        {"id": "f", "choices": ["cat", "cat"]},
        "Choice values are not unique",
    ),
    (
        {"id": "f", "choices": [1.1]},
        "Choices format not known",
    ),
]


@pytest.mark.parametrize("field_config, expected_error_message", test_bad_config_data)
def test_bad_config(field_config, expected_error_message):
    config = FieldEnumConfigModel()
    with pytest.raises(SiteConfigurationException) as excinfo:
        config.load(field_config)
    assert expected_error_message == str(excinfo.value)
