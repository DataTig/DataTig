class ErrorModel:
    def __init__(self):
        self.filename = None
        self.message = None

    def load_from_database(self, data: dict) -> None:
        self.filename = data["filename"]
        self.message = data["message"]
