class RecordJSONSchemaValidationErrorModel:
    def __init__(self):
        self.message = None
        self.data_path = None
        self.schema_path = None

    def load_from_database(self, data):
        self.message = data["message"]
        self.data_path = data["data_path"]
        self.schema_path = data["schema_path"]
