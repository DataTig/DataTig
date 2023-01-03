import json

from .record_error import RecordErrorModel
from .type import TypeModel


class RecordModel:
    def __init__(self, type=None, id=None):
        self._type: TypeModel = type
        self._id: str = id
        self._data = None
        self._git_filename = None
        self._errors = []
        self._format = None
        self._field_values: dict = {}

    def load_from_json_file(self, data: dict, git_filename: str) -> None:
        self._data = data
        for field_id, field_config in self._type.get_fields().items():
            self._field_values[field_id] = field_config.get_value_object_from_record(
                record=self
            )
        self._git_filename = git_filename
        self._format = "json"

    def load_from_yaml_file(self, data: dict, git_filename: str) -> None:
        self._data = data
        for field_id, field_config in self._type.get_fields().items():
            self._field_values[field_id] = field_config.get_value_object_from_record(
                record=self
            )
        self._git_filename = git_filename
        self._format = "yaml"

    def load_from_md_file(self, data: dict, git_filename: str) -> None:
        self._data = data
        for field_id, field_config in self._type.get_fields().items():
            self._field_values[field_id] = field_config.get_value_object_from_record(
                record=self
            )
        self._git_filename = git_filename
        self._format = "md"

    def load_from_database(self, data: dict, errors_data: list = None) -> None:
        self._data = json.loads(data["data"])
        for field_id, field_config in self._type.get_fields().items():
            self._field_values[field_id] = field_config.get_value_object_from_record(
                record=self
            )
        self._git_filename = data["git_filename"]
        self._format = data["format"]
        if errors_data is not None:
            for error_data in errors_data:
                m = RecordErrorModel()
                m.load_from_database(error_data)
                self._errors.append(m)

    def load_from_versioned_database(
        self, commit_type_record_row: dict, data_row: dict, errors_data: list = None
    ) -> None:
        self._data = json.loads(data_row["data"])
        for field_id, field_config in self._type.get_fields().items():
            self._field_values[field_id] = field_config.get_value_object_from_record(
                record=self
            )
        self._git_filename = commit_type_record_row["git_filename"]
        self._format = commit_type_record_row["format"]
        if errors_data is not None:
            for error_data in errors_data:
                m = RecordErrorModel()
                m.load_from_database(error_data)
                self._errors.append(m)

    def get_format(self) -> str:
        return self._format

    def get_git_filename(self) -> str:
        return self._git_filename

    def get_data(self) -> dict:
        return self._data

    def get_data_as_json_string(self) -> str:
        return json.dumps(self._data)

    def get_type(self) -> TypeModel:
        return self._type

    def get_id(self) -> str:
        return self._id

    def get_errors(self) -> list:
        return self._errors

    def get_field_value(self, field_id):
        return self._field_values.get(field_id)

    def get_diff(self, record) -> dict:
        out: dict = {}
        field_ids = list(
            set(list(self._field_values.keys()) + list(record._field_values.keys()))
        )
        for field_id in field_ids:
            if (
                field_id not in self._field_values.keys()
                and field_id in record._field_values.keys()
            ):
                out[field_id] = {"type": "added"}
            elif (
                field_id in self._field_values.keys()
                and field_id not in record._field_values.keys()
            ):
                out[field_id] = {"type": "removed"}
            elif type(self._field_values[field_id]) != type(
                record._field_values[field_id]
            ):
                out[field_id] = {"type": "different-type"}
            elif self._field_values[field_id].different_to(
                record._field_values[field_id]
            ):
                out[field_id] = {"type": "diff"}
            # No else clause - if field values are the same, we don't add any data to the output
        return out
