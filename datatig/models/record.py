import json


class RecordModel:
    def __init__(self):
        self.data = None
        self.git_filename = None
        self.json_schema_validation_errors = {}
        self.json_schema_validation_pass = False
        self.format = None

    def load_from_json_file(self, data, git_filename):
        self.data = data
        self.git_filename = git_filename
        self.format = "json"

    def load_from_yaml_file(self, data, git_filename):
        self.data = data
        self.git_filename = git_filename
        self.format = "yaml"

    def load_from_database(self, data):
        self.data = json.loads(data["data"])
        self.git_filename = data["git_filename"]
        self.format = data["format"]
        self.json_schema_validation_errors = json.loads(
            data["json_schema_validation_errors"]
        )
        self.json_schema_validation_pass = bool(data["json_schema_validation_errors"])
