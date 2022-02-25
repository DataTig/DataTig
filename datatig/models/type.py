import json
import os.path

from datatig.jsonschemabuilder import build_json_schema

from .type_field import get_type_field_model_for_type


class TypeModel:
    def __init__(self, siteconfig):
        self.id = None
        self.config = None
        self.fields = {}
        self.siteconfig = siteconfig

    def load_from_config(self, config) -> None:
        self.id = config.get("id")
        self.config = config
        self.fields = {}
        for config in self.config.get("fields", []):
            field_config = get_type_field_model_for_type(config.get("type"))
            field_config.load(config)
            self.fields[field_config.id] = field_config

    def directory(self) -> str:
        return self.config.get("directory")

    def directory_in_git_repository(self) -> str:
        dir = self.config.get("directory")
        if self.siteconfig.git_submodule_directory() and dir.startswith(
            self.siteconfig.git_submodule_directory()
        ):
            dir = dir[len(self.siteconfig.git_submodule_directory()) :]
        return dir

    def guide_form_xlsx(self) -> str:
        return self.config.get("guide_form_xlsx")

    def list_fields(self) -> list:
        return self.config.get("list_fields", [])  # TODO add some sensible defaults

    def json_schema_as_dict(self) -> dict:
        if self.config.get("json_schema"):
            with open(
                os.path.join(self.siteconfig.source_dir, self.config.get("json_schema"))
            ) as fp:
                return json.load(fp)
        else:
            results = build_json_schema(self.fields.values())
            return results.json_schema()

    def pretty_json_indent(self) -> int:
        return self.config.get("pretty_json_indent", 4)

    def default_format(self) -> str:
        return self.config.get("default_format", "yaml")

    def markdown_body_is_field(self) -> str:
        return self.config.get("markdown_body_is_field", "body")
