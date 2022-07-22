from abc import ABC


class FieldConfigModel(ABC):
    def __init__(self):
        self._id = None
        self._key = None
        self._title = None

    def load(self, config) -> None:
        self._id = config.get("id")
        self._title = config.get("title", self._id)
        self._key = config.get("key")

    def load_from_database(self, data) -> None:
        self._id = data["id"]
        self._title = data["title"]
        self._key = data["key"]

    def get_id(self) -> str:
        return self._id

    def get_key(self) -> str:
        return self._key

    def get_title(self) -> str:
        return self._title

    def get_frictionless_csv_field_specifications(self) -> list:
        return []

    def get_frictionless_csv_resource_specifications(self) -> list:
        return []


class FieldValueModel(ABC):
    def __init__(self, record=None, field_id=None):
        self._record = record
        self._field_id = field_id

    def get_frictionless_csv_data_values(self) -> list:
        """Should return a list of exactly the same number of elements as get_frictionless_csv_field_specifications() returns."""
        return []

    def get_frictionless_csv_resource_data_values(self, resource_name: str) -> list:
        """Should return a list of items. Each item should be a list of exactly the same number of elements as fields this resource has."""
        return []
