class RecordErrorModel:
    def __init__(self):
        self._record_id = None
        self._message = None
        self._data_path = None
        self._schema_path = None
        self._generator = None

    def load_from_database(self, data) -> None:
        self._record_id = data["record_id"]
        self._message = data["message"]
        self._data_path = data["data_path"]
        self._schema_path = data["schema_path"]
        self._generator = data["generator"]

    def get_record_id(self) -> str:
        return self._record_id

    def get_message(self) -> str:
        return self._message

    def get_data_path(self) -> str:
        return self._data_path

    def get_schema_path(self) -> str:
        return self._schema_path

    def get_generator(self) -> str:
        return self._generator
