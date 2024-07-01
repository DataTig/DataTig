import tempfile

from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel


def test_no_markdown_body_in_json():
    siteconfig = SiteConfigModel(tempfile.gettempdir())
    type = TypeModel(siteconfig)
    type.load_from_config(
        {
            "id": "test",
            "directory": "test/",
            "fields": [{"id": "title", "key": "title"}],
            "default_format": "json",
        }
    )
    assert type.get_markdown_body_is_field() is None


def test_default_markdown_body_in_md_does_not_exist():
    siteconfig = SiteConfigModel(tempfile.gettempdir())
    type = TypeModel(siteconfig)
    type.load_from_config(
        {
            "id": "test",
            "directory": "test/",
            "fields": [{"id": "title", "key": "title"}],
            "default_format": "md",
        }
    )
    # Default field is set
    assert type.get_markdown_body_is_field() == "body"
    # And as it doesn't already exist, it's created for us.
    assert type.get_field("body") is not None


def test_default_markdown_body_in_md_exists():
    siteconfig = SiteConfigModel(tempfile.gettempdir())
    type = TypeModel(siteconfig)
    type.load_from_config(
        {
            "id": "test",
            "directory": "test/",
            "fields": [
                {"id": "title", "key": "title"},
                {"id": "body", "key": "body", "title": "Ours"},
            ],
            "default_format": "md",
        }
    )
    # Default field is set
    assert type.get_markdown_body_is_field() == "body"
    # And as it already exists, our definition is used
    assert type.get_field("body").get_title() == "Ours"


def test_default_markdown_body_in_md_can_be_blocked():
    siteconfig = SiteConfigModel(tempfile.gettempdir())
    type = TypeModel(siteconfig)
    type.load_from_config(
        {
            "id": "test",
            "directory": "test/",
            "fields": [{"id": "title", "key": "title"}],
            "default_format": "md",
            "markdown_body_is_field": "---",
        }
    )
    # Default field is not set
    assert type.get_markdown_body_is_field() is None
    # And no new fields are added
    assert len(type.get_fields().keys()) == 1
