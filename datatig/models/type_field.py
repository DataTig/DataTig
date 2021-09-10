class TypeFieldModel:
    def __init__(self):
        self.id = None
        self._key = None
        self._type = None
        self._title = None

    def load(self, config) -> None:
        self.id = config.get("id")
        self._type = config.get("type", "string")
        self._title = config.get("title", self.id)
        self._key = config.get("key")

    def load_from_database(self, data) -> None:
        self.id = data["id"]
        self._type = data["type"]
        self._title = data["title"]
        self._key = data["key"]

    def key(self) -> str:
        return self._key

    def type(self) -> str:
        return self._type

    def title(self) -> str:
        return self._title
