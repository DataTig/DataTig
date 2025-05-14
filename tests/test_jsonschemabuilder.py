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
    field1._load_extra_config({})
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "title": {"title": "Title", "description": "", "type": "string"}
        },
        "type": "object",
    } == result.get_json_schema()


def test_string_min_max_length():
    field1 = FieldStringConfigModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    field1._load_extra_config({"min_length": 5, "max_length": 10})
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "title": {
                "title": "Title",
                "description": "",
                "type": "string",
                "min_length": 5,
                "max_length": 10,
            }
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


def test_list_strings_min_max_length():
    field1 = FieldListStringsConfigModel()
    field1.id = "tags"
    field1._key = "tags"
    field1._title = "Tags"
    field1._load_extra_config({"string_min_length": 10, "string_max_length": 50})
    fields = [field1]
    result = build_json_schema(fields)
    assert {
        "$schema": "http://json-schema.org/draft-07/schema",
        "properties": {
            "tags": {
                "items": {"type": "string", "min_length": 10, "max_length": 50},
                "title": "Tags",
                "description": "",
                "type": "array",
                "uniqueItems": False,
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_list_strings():
    field1 = FieldListStringsConfigModel()
    field1.id = "tags"
    field1._key = "tags"
    field1._title = "Tags"
    field1._load_extra_config({})
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
                "uniqueItems": False,
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_list_strings_unique():
    field1 = FieldListStringsConfigModel()
    field1.id = "tags"
    field1._key = "tags"
    field1._title = "Tags"
    field1._load_extra_config({"unique_items": True})
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
                "uniqueItems": True,
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_all_types_at_once():
    field1 = FieldStringConfigModel()
    field1.id = "title"
    field1._key = "title"
    field1._title = "Title"
    field1._load_extra_config({})
    field2 = FieldURLConfigModel()
    field2.id = "url"
    field2._key = "url"
    field2._title = "URL"
    field3 = FieldListStringsConfigModel()
    field3.id = "tags"
    field3._key = "tags"
    field3._title = "Tags"
    field3._load_extra_config({})
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
                "uniqueItems": False,
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
    field1._load_extra_config({})
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
    field1._load_extra_config({})
    field2 = FieldURLConfigModel()
    field2.id = "url"
    field2._key = "information/url"
    field2._title = "URL"
    field3 = FieldListStringsConfigModel()
    field3.id = "tags"
    field3._key = "information/labelling/tags"
    field3._title = "Tags"
    field3._load_extra_config({})
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
                                "uniqueItems": False,
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
    field = FieldListDictionariesConfigModel()
    field.id = "musicians"
    field._key = "musicians"
    field._title = "Musicians"
    field._load_extra_config(
        {
            "fields": [
                {"id": "url", "key": "information/url", "title": "URL", "type": "url"},
                {"id": "formal_name", "key": "names/formal", "title": "Formal Name"},
            ]
        }
    )
    result = build_json_schema([field])
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
                "uniqueItems": False,
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_list_dictionaries_unique():
    field = FieldListDictionariesConfigModel()
    field.id = "musicians"
    field._key = "musicians"
    field._title = "Musicians"
    field._load_extra_config(
        {
            "fields": [
                {"id": "url", "key": "information/url", "title": "URL", "type": "url"},
            ],
            "unique_items": True,
        }
    )
    result = build_json_schema([field])
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
                    },
                    "type": "object",
                },
                "title": "Musicians",
                "description": "",
                "type": "array",
                "uniqueItems": True,
            }
        },
        "type": "object",
    } == result.get_json_schema()
