import hashlib
import json

import yaml

from datatig.exceptions import (
    SiteConfigurationException,
    SiteConfigurationNotFoundException,
)
from datatig.models.calendar import CalendarModel
from datatig.models.type import TypeModel
from datatig.repository_access import RepositoryAccess


class SiteConfigModel:
    def __init__(self, source_dir: str):
        self._config: dict = {}
        self._types: dict = {}
        self._source_dir: str = source_dir
        self._calendars: dict = {}

    def load_from_file(self, repository_access: RepositoryAccess) -> None:
        if repository_access.has_file("datatig.json"):
            self._config = json.loads(
                repository_access.get_contents_of_file("datatig.json")
            )
        elif repository_access.has_file("datatig.yaml"):
            self._config = yaml.safe_load(
                repository_access.get_contents_of_file("datatig.yaml")
            )
        else:
            raise SiteConfigurationNotFoundException("No Config File!")
        self._after_load()

    def load_from_serialised(self, config: dict):
        self._config = config
        self._after_load()

    def _after_load(self):
        for type_config in self._config.get("types", []):
            type_config_model = TypeModel(self)
            type_config_model.load_from_config(type_config)
            if type_config_model.get_id() in self._types:
                raise SiteConfigurationException(
                    "More than one type with the same id {}".format(
                        type_config_model.get_id()
                    )
                )
            self._types[type_config_model.get_id()] = type_config_model
        for calendar_id, calendar_config in self._config.get("calendars", {}).items():
            calendar_config_model = CalendarModel(self)
            calendar_config_model.load_from_config(calendar_id, calendar_config)
            self._calendars[calendar_id] = calendar_config_model

    def get_github_url(self) -> str:
        return self._config.get("githost", {}).get("url")

    def get_githost_primary_branch(self) -> str:
        return self._config.get("githost", {}).get("primary_branch", "main")

    def get_githost_directory(self) -> str:
        """Always returns an empty string if no directory.
        Or if directory, always returns string with no slash at start and a slash at the end.
        This makes it suitable for dropping into URLs with no further checking."""
        x = self._config.get("githost", {}).get("directory", "") or ""
        if x.startswith("/"):
            x = x[1:]
        if x and not x.endswith("/"):
            x = x + "/"
        return x

    def get_types(self) -> dict:
        return self._types

    def get_type(self, type_id: str):
        return self._types.get(type_id)

    def get_calendars(self) -> dict:
        return self._calendars

    def get_calendar(self, calendar_id: str):
        return self._calendars.get(calendar_id)

    def get_source_dir(self) -> str:
        return self._source_dir

    def get_title(self) -> str:
        return self._config.get("title", "SITE")

    def get_description(self) -> str:
        return self._config.get("description", "")

    def get_serialised(self) -> dict:
        return self._config

    def get_hash(self) -> str:
        return hashlib.md5(
            json.dumps(self.get_serialised(), default=str, sort_keys=True).encode(
                "utf-8"
            )
        ).hexdigest()
