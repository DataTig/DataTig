import json
import os.path
from typing import Optional

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
from .field_markdown import FieldMarkdownConfigModel
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
        if self.get_record_id_mode() not in ["directory_and_filename", "filename_only"]:
            raise SiteConfigurationException(
                "Unknown Record ID mode in type {}".format(self._id)
            )
        # Fields
        self._fields = {}
        for config in self._config.get("fields", []):
            field_config: FieldConfigModel = FieldStringConfigModel()
            field_type: str = str(config.get("type", "string")).lower().strip()
            if field_type == "url":
                field_config = FieldURLConfigModel()
            elif field_type == "list-strings":
                field_config = FieldListStringsConfigModel()
            elif field_type == "list-dictionaries" or field_type == "list-dicts":
                field_config = FieldListDictionariesConfigModel()
            elif field_type == "date":
                field_config = FieldDateConfigModel()
            elif field_type == "datetime":
                field_config = FieldDateTimeConfigModel()
            elif field_type == "boolean":
                field_config = FieldBooleanConfigModel()
            elif field_type == "integer":
                field_config = FieldIntegerConfigModel()
            elif field_type == "markdown":
                field_config = FieldMarkdownConfigModel()
            elif field_type and field_type != "string":
                raise SiteConfigurationException(
                    "Unknown field type {} in field {} in type {}".format(
                        field_type, field_config.get_id(), self._id
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
        # Maybe add a field automatically for Markdown body?
        markdown_body_is_field = self.get_markdown_body_is_field()
        if markdown_body_is_field and not markdown_body_is_field in self._fields:
            self._fields[markdown_body_is_field] = FieldMarkdownConfigModel()
            self._fields[markdown_body_is_field].load(
                {
                    "id": markdown_body_is_field,
                    "title": "Body of the markdown file",
                    "description": "The body of the markdown file. Markdown can be used in this.",
                    "key": markdown_body_is_field,
                }
            )

    def get_directory(self) -> str:
        return self._config.get("directory")

    def get_directory_in_git_repository(self) -> str:
        return self._config.get("directory")

    def get_list_fields(self) -> list:
        if self._config.get("list_fields"):
            return self._config.get("list_fields")
        elif self._fields:
            return [list(self._fields)[0]]
        else:
            return []

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

    def get_markdown_body_is_field(self) -> Optional[str]:
        x = self._config.get("markdown_body_is_field")
        if x:
            # If user has specified a value, use that.
            # Or allow a special value to override
            return x if x != "---" else None
        elif self.get_default_format() == "md":
            # If md is the standard format, we want a field to hold body.
            return "body"
        else:
            return None

    def get_record_id_mode(self) -> str:
        return (
            str(self._config.get("record_id_mode", "directory_and_filename"))
            .lower()
            .strip()
        )

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
