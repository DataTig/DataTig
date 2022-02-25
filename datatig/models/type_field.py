class TypeFieldModel:
    def __init__(self):
        self.id = None
        self._key = None
        self._title = None

    def load(self, config) -> None:
        self.id = config.get("id")
        self._title = config.get("title", self.id)
        self._key = config.get("key")

    def load_from_database(self, data) -> None:
        self.id = data["id"]
        self._title = data["title"]
        self._key = data["key"]

    def key(self) -> str:
        return self._key

    def title(self) -> str:
        return self._title


class TypeStringFieldModel(TypeFieldModel):
    def type(self) -> str:
        return "string"

    def json_schema(self) -> dict:
        return {
            "type": "string",
            "title": self._title,
        }


class TypeURLFieldModel(TypeFieldModel):
    def type(self) -> str:
        return "url"

    def json_schema(self) -> dict:
        return {
            "type": "string",
            "format": "uri",
            "title": self._title,
        }


class TypeListStringsFieldModel(TypeFieldModel):
    def type(self) -> str:
        return "list-strings"

    def json_schema(self) -> dict:
        return {"title": self._title, "type": "array", "items": {"type": "string"}}


def get_type_field_model_for_type(type: str) -> TypeFieldModel:
    if type == "url":
        return TypeURLFieldModel()
    elif type == "list-strings":
        return TypeListStringsFieldModel()
    else:
        return TypeStringFieldModel()
