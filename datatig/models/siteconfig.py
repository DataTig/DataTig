import json
import os

import yaml

from datatig.models.type import TypeModel


class SiteConfigModel:
    def __init__(self, source_dir: str):
        self._config: dict = {}
        self._types: dict = {}
        self._source_dir: str = source_dir

    def load_from_file(self) -> None:

        if os.path.isfile(os.path.join(self._source_dir, "datatig.json")):
            with open(os.path.join(self._source_dir, "datatig.json")) as fp:
                self._config = json.load(fp)
        elif os.path.isfile(os.path.join(self._source_dir, "datatig.yaml")):
            with open(os.path.join(self._source_dir, "datatig.yaml")) as fp:
                self._config = yaml.safe_load(fp)
        else:
            raise Exception("No Config File!")

        for type_config in self._config.get("types", []):
            type_config_model = TypeModel(self)
            type_config_model.load_from_config(type_config)
            self._types[type_config_model.get_id()] = type_config_model

    def get_github_url(self) -> str:
        return self._config.get("githost", {}).get("url")

    def get_githost_primary_branch(self) -> str:
        return self._config.get("githost", {}).get("primary_branch", "main")

    def get_types(self) -> dict:
        return self._types

    def get_type(self, type_id: str):
        return self._types.get(type_id)

    def get_source_dir(self) -> str:
        return self._source_dir

    def get_title(self) -> str:
        return self._config.get("title", "SITE")

    def get_description(self) -> str:
        return self._config.get("description", "")
