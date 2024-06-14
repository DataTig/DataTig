from datatig.jsonschemabuilder import build_json_schema
from datatig.models.field_list_dictionaries import FieldListDictionariesConfigModel
from datatig.models.field_list_strings import FieldListStringsConfigModel
from datatig.models.field_string import FieldStringConfigModel
from datatig.models.field_url import FieldURLConfigModel


def test_string():
    field1 = FieldStringConfigModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "title": {"title": "Title", "description": "", "type": "string"}
        },
        "type": "object",
    } == result.get_json_schema()


def test_url():
    field1 = FieldURLConfigModel()
    field1.id = "url"
    field1._key = "url"
    field1._title = "URL"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "url": {
                "format": "uri",
                "title": "URL",
                "description": "",
                "type": "string",
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_list_strings():
    field1 = FieldListStringsConfigModel()
    field1.id = "tags"
    field1._key = "tags"
    field1._title = "Tags"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "tags": {
                "items": {"type": "string"},
                "title": "Tags",
                "description": "",
                "type": "array",
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_all_types_at_once():
    field1 = FieldStringConfigModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    field2 = FieldURLConfigModel()
    field2.id = "url"
    field2._key = "url"
    field2._title = "URL"
    field3 = FieldListStringsConfigModel()
    field3.id = "tags"
    field3._key = "tags"
    field3._title = "Tags"
    fields = [field1, field2, field3]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "tags": {
                "items": {"type": "string"},
                "title": "Tags",
                "description": "",
                "type": "array",
            },
            "title": {"title": "Title", "description": "", "type": "string"},
            "url": {
                "format": "uri",
                "title": "URL",
                "description": "",
                "type": "string",
            },
        },
        "type": "object",
    } == result.get_json_schema()


def test_1_layer_deep():
    field1 = FieldStringConfigModel()
    field1.id = "title_en"
    field1._key = "title/en"
    field1._title = "Title (En)"
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "title": {
                "properties": {
                    "en": {"title": "Title (En)", "description": "", "type": "string"}
                },
                "type": "object",
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_root_and_many_layers_deep_at_once():
    field1 = FieldStringConfigModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    field2 = FieldURLConfigModel()
    field2.id = "url"
    field2._key = "information/url"
    field2._title = "URL"
    field3 = FieldListStringsConfigModel()
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
                                "description": "",
                                "type": "array",
                            }
                        },
                        "type": "object",
                    },
                    "url": {
                        "format": "uri",
                        "title": "URL",
                        "description": "",
                        "type": "string",
                    },
                },
                "type": "object",
            },
            "title": {"title": "Title", "description": "", "type": "string"},
        },
        "type": "object",
    } == result.get_json_schema()


def test_list_dictionaries():
    field1 = FieldListDictionariesConfigModel()
    field1.id = "musicians"
    field1._key = "musicians"
    field1._title = "Musicians"
    field2 = FieldURLConfigModel()
    field2.id = "url"
    field2._key = "information/url"
    field2._title = "URL"
    field1._fields["url"] = field2
    field3 = FieldStringConfigModel()
    field3.id = "formal_name"
    field3._key = "names/formal"
    field3._title = "Formal Name"
    field1._fields["formal_name"] = field3
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "musicians": {
                "items": {
                    "properties": {
                        "information": {
                            "properties": {
                                "url": {
                                    "format": "uri",
                                    "title": "URL",
                                    "description": "",
                                    "type": "string",
                                }
                            },
                            "type": "object",
                        },
                        "names": {
                            "properties": {
                                "formal": {
                                    "title": "Formal Name",
                                    "description": "",
                                    "type": "string",
                                }
                            },
                            "type": "object",
                        },
                    },
                    "type": "object",
                },
                "title": "Musicians",
                "description": "",
                "type": "array",
            }
        },
        "type": "object",
    } == result.get_json_schema()
