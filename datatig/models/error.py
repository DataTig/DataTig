class ErrorModel:
    def __init__(self, filename=None, message=None):
        self._filename = filename
        self._message = message

    def load_from_database(self, data: dict) -> None:
        self._filename = data["filename"]
        self._message = data["message"]

    def get_filename(self) -> str:
        return self._filename

    def get_message(self) -> str:
        return self._message
