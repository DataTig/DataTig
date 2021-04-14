class TypeFieldModel:
    def __init__(self):
        self.id = None
        self._key = None
        self._type = None
        self._title = None

    def load(self, config):
        self.id = config.get("id")
        self._type = config.get("type", "string")
        self._title = config.get("title", self.id)
        self._key = config.get("key")

    def load_from_database(self, data):
        self.id = data["id"]
        self._type = data["type"]
        self._title = data["title"]
        self._key = data["key"]

    def key(self):
        return self._key

    def type(self):
        return self._type

    def title(self):
        return self._title
