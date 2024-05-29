import os
import tempfile

import pytest

import datatig.process
from datatig.exceptions import SiteConfigurationException

test_site_configuration_exception_data = [
    ("duplicate_type_id", "More than one type with the same id datas"),
    ("duplicate_field_id", "More than one field with the same id title in type datas"),
]


@pytest.mark.parametrize(
    "directory_name, expected_error", test_site_configuration_exception_data
)
def test_site_configuration_exception(directory_name, expected_error):
    with tempfile.TemporaryDirectory() as staticsite_dir:
        with pytest.raises(SiteConfigurationException) as exc_info:
            datatig.process.go(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "data",
                    "site_configuration_exception",
                    directory_name,
                ),
                sqlite_output=os.path.join(
                    staticsite_dir,
                    "db.sqlite",
                ),
            )
    assert str(exc_info.value) == expected_error
