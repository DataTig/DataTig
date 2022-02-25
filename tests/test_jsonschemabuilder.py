from datatig.jsonschemabuilder import build_json_schema
from datatig.models.type_field import (
    TypeListStringsFieldModel,
    TypeStringFieldModel,
    TypeURLFieldModel,
)


def test_string():
    field1 = TypeStringFieldModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {"title": {"title": "Title", "type": "string"}},
        "type": "object",
    } == result.json_schema()


def test_url():
    field1 = TypeURLFieldModel()
    field1.id = "url"
    field1._key = "url"
    field1._title = "URL"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {"url": {"format": "uri", "title": "URL", "type": "string"}},
        "type": "object",
    } == result.json_schema()


def test_list_strings():
    field1 = TypeListStringsFieldModel()
    field1.id = "tags"
    field1._key = "tags"
    field1._title = "Tags"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "tags": {"items": {"type": "string"}, "title": "Tags", "type": "array"}
        },
        "type": "object",
    } == result.json_schema()


def test_all_types_at_once():
    field1 = TypeStringFieldModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    field2 = TypeURLFieldModel()
    field2.id = "url"
    field2._key = "url"
    field2._title = "URL"
    field3 = TypeListStringsFieldModel()
    field3.id = "tags"
    field3._key = "tags"
    field3._title = "Tags"
    fields = [field1, field2, field3]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "tags": {"items": {"type": "string"}, "title": "Tags", "type": "array"},
            "title": {"title": "Title", "type": "string"},
            "url": {"format": "uri", "title": "URL", "type": "string"},
        },
        "type": "object",
    } == result.json_schema()


def test_1_layer_deep():
    field1 = TypeStringFieldModel()
    field1.id = "title_en"
    field1._key = "title/en"
    field1._title = "Title (En)"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "title": {
                "properties": {"en": {"title": "Title (En)", "type": "string"}},
                "type": "object",
            }
        },
        "type": "object",
    } == result.json_schema()


def test_root_and_many_layers_deep_at_once():
    field1 = TypeStringFieldModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    field2 = TypeURLFieldModel()
    field2.id = "url"
    field2._key = "information/url"
    field2._title = "URL"
    field3 = TypeListStringsFieldModel()
    field3.id = "tags"
    field3._key = "information/labelling/tags"
    field3._title = "Tags"
    fields = [field1, field2, field3]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "information": {
                "properties": {
                    "labelling": {
                        "properties": {
                            "tags": {
                                "items": {"type": "string"},
                                "title": "Tags",
                                "type": "array",
                            }
                        },
                        "type": "object",
                    },
                    "url": {"format": "uri", "title": "URL", "type": "string"},
                },
                "type": "object",
            },
            "title": {"title": "Title", "type": "string"},
        },
        "type": "object",
    } == result.json_schema()
