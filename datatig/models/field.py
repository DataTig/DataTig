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


class FieldValueModel(ABC):
    def __init__(self, record=None, field_id=None):
        self._record = record
        self._field_id = field_id
