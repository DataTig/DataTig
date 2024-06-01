import json
import os.path

from datatig.exceptions import SiteConfigurationException
from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.jsonschemabuilder import build_json_schema

from .field import FieldConfigModel
from .field_boolean import FieldBooleanConfigModel
from .field_date import FieldDateConfigModel
from .field_datetime import FieldDateTimeConfigModel
from .field_integer import FieldIntegerConfigModel
from .field_list_dictionaries import FieldListDictionariesConfigModel
from .field_list_strings import FieldListStringsConfigModel
from .field_string import FieldStringConfigModel
from .field_url import FieldURLConfigModel


class TypeModel:
    def __init__(self, siteconfig):
        self._id = None
        self._config = None
        self._fields = {}
        self._siteconfig = siteconfig
        self._cached_json_schema = None

    def load_from_config(self, config) -> None:
        self._id = config.get("id")
        self._config = config
        self._fields = {}
        for config in self._config.get("fields", []):
            field_config: FieldConfigModel = FieldStringConfigModel()
            if config.get("type") == "url":
                field_config = FieldURLConfigModel()
            elif config.get("type") == "list-strings":
                field_config = FieldListStringsConfigModel()
            elif (
                config.get("type") == "list-dictionaries"
                or config.get("type") == "list-dicts"
            ):
                field_config = FieldListDictionariesConfigModel()
            elif config.get("type") == "date":
                field_config = FieldDateConfigModel()
            elif config.get("type") == "datetime":
                field_config = FieldDateTimeConfigModel()
            elif config.get("type") == "boolean":
                field_config = FieldBooleanConfigModel()
            elif config.get("type") == "integer":
                field_config = FieldIntegerConfigModel()
            elif config.get("type") and config.get("type") != "string":
                raise SiteConfigurationException(
                    "Unknown field type {} in field {} in type {}".format(
                        config.get("type"), field_config.get_id(), self._id
                    )
                )
            field_config.load(config)
            if field_config.get_id() in self._fields:
                raise SiteConfigurationException(
                    "More than one field with the same id {} in type {}".format(
                        field_config.get_id(), self._id
                    )
                )
            self._fields[field_config.get_id()] = field_config

    def get_directory(self) -> str:
        return self._config.get("directory")

    def get_directory_in_git_repository(self) -> str:
        return self._config.get("directory")

    def get_list_fields(self) -> list:
        return self._config.get("list_fields", [])  # TODO add some sensible defaults

    def get_json_schema_as_dict(self) -> dict:
        if not self._cached_json_schema:
            if self._config.get("json_schema"):
                with open(
                    os.path.join(
                        self._siteconfig.get_source_dir(),
                        self._config.get("json_schema"),
                    )
                ) as fp:
                    self._cached_json_schema = json.load(fp)
            else:
                results = build_json_schema(self._fields.values())
                self._cached_json_schema = results.get_json_schema()
        return self._cached_json_schema

    def get_json_schema_as_string(self) -> str:
        return json.dumps(self.get_json_schema_as_dict())

    def get_pretty_json_indent(self) -> int:
        return self._config.get("pretty_json_indent", 4)

    def get_default_format(self) -> str:
        return self._config.get("default_format", "yaml")

    def get_markdown_body_is_field(self) -> str:
        return self._config.get("markdown_body_is_field", "body")

    def get_new_item_json(self) -> dict:
        out: JSONDeepReaderWriter = JSONDeepReaderWriter({})
        for field in self._fields.values():
            out.write(field.get_key(), field.get_new_item_json())
        return out.get_json()

    def get_new_item_json_as_string(self) -> str:
        return json.dumps(self.get_new_item_json())

    def get_id(self) -> str:
        return self._id

    def get_fields(self) -> dict:
        return self._fields

    def get_field(self, field_id) -> FieldConfigModel:
        return self._fields.get(field_id)
