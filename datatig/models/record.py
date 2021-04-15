import json

from .record_json_schema_validation_error import RecordJSONSchemaValidationErrorModel


class RecordModel:
    def __init__(self):
        self.data = None
        self.git_filename = None
        self.json_schema_validation_errors = []
        self.json_schema_validation_pass = None
        self.format = None

    def load_from_json_file(self, data, git_filename):
        self.data = data
        self.git_filename = git_filename
        self.format = "json"

    def load_from_yaml_file(self, data, git_filename):
        self.data = data
        self.git_filename = git_filename
        self.format = "yaml"

    def load_from_database(self, data, json_schema_validation_errors_data=None):
        self.data = json.loads(data["data"])
        self.git_filename = data["git_filename"]
        self.format = data["format"]
        if json_schema_validation_errors_data is not None:
            if json_schema_validation_errors_data:
                for (
                    json_schema_validation_error_data
                ) in json_schema_validation_errors_data:
                    m = RecordJSONSchemaValidationErrorModel()
                    m.load_from_database(json_schema_validation_error_data)
                    self.json_schema_validation_errors.append(m)
                self.json_schema_validation_pass = False
            else:
                self.json_schema_validation_pass = True
