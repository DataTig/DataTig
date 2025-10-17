from abc import ABC, abstractmethod


class FieldConfigModel(ABC):
    def __init__(self):
        self._id = None
        self._key = None
        self._title = None
        self._description: str = ""
        self._required: bool = False
        self._extra_config = {}

    def load(self, config: dict) -> None:
        self._id = config.get("id")
        self._title = config.get("title", self._id)
        self._description = config.get("description", "")
        self._key = config.get("key", self._id)
        self._required = bool(config.get("required", False))
        self._load_extra_config(config)

    def _load_extra_config(self, config: dict) -> None:
        pass

    def load_from_database(self, data) -> None:
        self._id = data["id"]
        self._title = data["title"]
        self._description = data["description"]
        self._key = data["key"]
        self._required = data["required"]

    def get_id(self) -> str:
        return self._id

    def get_key(self) -> str:
        return self._key

    def get_title(self) -> str:
        return self._title

    def get_description(self) -> str:
        return self._description

    def get_required(self) -> bool:
        return self._required

    def get_extra_config(self) -> dict:
        return self._extra_config

    def get_value_object(self, record, data):
        pass

    def get_frictionless_csv_field_specifications(self) -> list:
        return []

    def get_frictionless_csv_resource_specifications(self) -> list:
        return []

    def get_json_schema(self) -> dict:
        return {}


class FieldValueModel(ABC):
    def __init__(
        self,
        field: FieldConfigModel,
        record=None,
    ):
        self._record = record
        self._field = field

    @abstractmethod
    def has_value(self) -> bool:
        pass

    def get_frictionless_csv_data_values(self) -> list:
        """Should return a list of exactly the same number of elements as get_frictionless_csv_field_specifications() returns."""
        return []

    def get_frictionless_csv_resource_data_values(self, resource_name: str) -> list:
        """Should return a list of items. Each item should be a list of exactly the same number of elements as fields this resource has."""
        return []

    @abstractmethod
    def different_to(self, other_field_value):
        pass

    @abstractmethod
    def get_api_value(self) -> dict:
        pass

    def get_urls_in_value(self) -> list:
        return []
