import os

import pytest

from datatig.models.siteconfig import SiteConfigModel


def test_get_githost_directory_none():
    config = SiteConfigModel(os.getcwd())
    config.load_from_serialised({})
    assert "" == config.get_githost_directory()


@pytest.mark.parametrize(
    "value, expected",
    [
        ("src", "src/"),
        ("src/", "src/"),
        ("/src", "src/"),
        ("/src/", "src/"),
        ("/src/a", "src/a/"),
    ],
)
def test_get_githost_directory_value(value, expected):
    config = SiteConfigModel(os.getcwd())
    config.load_from_serialised({"githost": {"directory": value}})
    assert expected == config.get_githost_directory()
