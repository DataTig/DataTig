import os
import tempfile

import pytest

import datatig.process
from datatig.exceptions import SiteConfigurationException

test_site_configuration_exception_data = [
    ("duplicate_type_id", "More than one type with the same id datas"),
    ("duplicate_field_id", "More than one field with the same id title in type datas"),
    ("unknown_field_type", "Unknown field type h1 in field None in type datas"),
    (
        "date_unknown_timezone",
        "Date field start has unknown timezone eueoaueoaueou/udiheeidideidiedu",
    ),
    (
        "datetime_unknown_timezone",
        "DateTime field start has unknown timezone eueoaueoaueou/udiheeidideidiedu",
    ),
    (
        "calendar_unknown_timezone",
        "Calendar main has unknown timezone eueoaueoaueou/udiheeidideidiedu",
    ),
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
