from datatig.jsonschemabuilder import build_json_schema
from datatig.models.field_list_dictionaries import FieldListDictionariesConfigModel
from datatig.models.field_list_strings import FieldListStringsConfigModel
from datatig.models.field_string import FieldStringConfigModel
from datatig.models.field_url import FieldURLConfigModel


def test_string():
    field1 = FieldStringConfigModel()
    field1.load({"id": "title", "key": "title", "title": "Title"})
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "properties": {
            "title": {"title": "Title", "description": "", "type": "string"}
        },
        "type": "object",
    } == result.get_json_schema()


def test_string_min_max_length():
    field1 = FieldStringConfigModel()
    field1.load(
        {
            "id": "title",
            "key": "title",
            "title": "Title",
            "min_length": 5,
            "max_length": 10,
        }
    )
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "properties": {
            "title": {
                "title": "Title",
                "description": "",
                "type": "string",
                "minLength": 5,
                "maxLength": 10,
            }
        },
        "type": "object",
    } == result.get_json_schema()


def test_url():
    field1 = FieldURLConfigModel()
    field1.load({"id": "url", "key": "url", "title": "URL"})
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field1.load(
        {
            "id": "tags",
            "key": "tags",
            "title": "Tags",
            "string_min_length": 10,
            "string_max_length": 50,
        }
    )
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "properties": {
            "tags": {
                "items": {"type": "string", "minLength": 10, "maxLength": 50},
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
    field1.load({"id": "tags", "key": "tags", "title": "Tags"})
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field1.load({"id": "tags", "key": "tags", "title": "Tags", "unique_items": True})
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field1.load({"id": "title", "key": "title", "title": "Title"})
    field2 = FieldURLConfigModel()
    field2.load({"id": "url", "key": "url", "title": "URL"})
    field3 = FieldListStringsConfigModel()
    field3.load({"id": "tags", "key": "tags", "title": "Tags"})
    result = build_json_schema([field1, field2, field3])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field1.load({"id": "title_en", "key": "title/en", "title": "Title (En)"})
    result = build_json_schema([field1])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field1.load({"id": "title", "key": "title", "title": "Title"})
    field2 = FieldURLConfigModel()
    field2.load({"id": "url", "key": "information/url", "title": "URL"})
    field3 = FieldListStringsConfigModel()
    field3.load({"id": "tags", "key": "information/labelling/tags", "title": "Tags"})
    result = build_json_schema([field1, field2, field3])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field.load(
        {
            "id": "musicians",
            "key": "musicians",
            "title": "Musicians",
            "fields": [
                {"id": "url", "key": "information/url", "title": "URL", "type": "url"},
                {"id": "formal_name", "key": "names/formal", "title": "Formal Name"},
            ],
        }
    )
    result = build_json_schema([field])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
    field.load(
        {
            "id": "musicians",
            "key": "musicians",
            "title": "Musicians",
            "fields": [
                {"id": "url", "key": "information/url", "title": "URL", "type": "url"},
            ],
            "unique_items": True,
        }
    )
    result = build_json_schema([field])
    assert {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
