import typing

from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.jsonschemabuilder import build_json_schema
from datatig.models.field import FieldConfigModel, FieldValueModel

from .field_boolean import FieldBooleanConfigModel
from .field_date import FieldDateConfigModel
from .field_datetime import FieldDateTimeConfigModel
from .field_integer import FieldIntegerConfigModel
from .field_string import FieldStringConfigModel
from .field_url import FieldURLConfigModel


class FieldListDictionariesConfigModel(FieldConfigModel):
    def __init__(self):
        super().__init__()
        self._fields = {}

    def get_type(self) -> str:
        return "list-dictionaries"

    def get_json_schema(self) -> dict:
        build_results = build_json_schema(self._fields.values(), child_schema=True)
        return {
            "title": self._title,
            "description": self._description,
            "type": "array",
            "items": build_results.get_json_schema(),
        }

    def _load_extra_config(self, config: dict) -> None:
        for config in config.get("fields", []):
            field_config: FieldConfigModel = FieldStringConfigModel()
            if config.get("type") == "url":
                field_config = FieldURLConfigModel()
            elif config.get("type") == "date":
                field_config = FieldDateConfigModel()
            elif config.get("type") == "datetime":
                field_config = FieldDateTimeConfigModel()
            elif config.get("type") == "boolean":
                field_config = FieldBooleanConfigModel()
            elif config.get("type") == "integer":
                field_config = FieldIntegerConfigModel()
            field_config.load(config)
            self._fields[field_config.get_id()] = field_config

    def get_new_item_json(self):
        return []

    def get_value_object(self, record, data):
        obj = JSONDeepReaderWriter(data)
        new_data = obj.read(self._key)
        v = FieldListDictionariesValueModel(field=self, record=record)
        if isinstance(new_data, list):
            for item_data in new_data:
                if isinstance(item_data, dict):
                    sub_record = FieldListDictionariesSubRecordModel()
                    for field in self._fields.values():
                        sub_record.set_value(
                            field.get_id(), field.get_value_object(record, item_data)
                        )
                    v.add_sub_record(sub_record)
        return v

    def get_frictionless_csv_field_specifications(self):
        return []

    def get_frictionless_csv_resource_specifications(self) -> list:
        out = {
            "name": "values",
            "fields": [],
        }
        for field in self._fields.values():
            out["fields"].extend(field.get_frictionless_csv_field_specifications())  # type: ignore
        return [out]

    def get_fields(self) -> dict:
        return self._fields


class FieldListDictionariesSubRecordModel:
    def __init__(self):
        self._fields = {}

    def set_value(self, field_id, value):
        self._fields[field_id] = value

    def get_value(self, field_id):
        return self._fields[field_id]


class FieldListDictionariesValueModel(FieldValueModel):
    def __init__(
        self,
        field: FieldConfigModel,
        record=None,
    ):
        super().__init__(field=field, record=record)
        self._sub_records: typing.List[FieldListDictionariesSubRecordModel] = []

    def add_sub_record(self, sub_record: FieldListDictionariesSubRecordModel):
        self._sub_records.append(sub_record)

    def get_value(self):
        return "LIST OF " + str(len(self._sub_records)) + " SUB RECORDS"

    def get_sub_records(self) -> typing.List[FieldListDictionariesSubRecordModel]:
        return self._sub_records

    def get_frictionless_csv_data_values(self):
        return []

    def get_frictionless_csv_resource_data_values(self, resource_name: str) -> list:
        out = []
        for sub_record in self._sub_records:
            sub_record_out = []
            for field in self._field.get_fields().values():  # type: ignore
                sub_record_out.extend(
                    sub_record.get_value(
                        field.get_id()
                    ).get_frictionless_csv_data_values()
                )
            out.append(sub_record_out)
        return out

    def different_to(self, other_field_value):
        if len(self._sub_records) != len(other_field_value._sub_records):
            return True
        for idx, x in enumerate(self._sub_records):
            for field in self._field.get_fields().values():
                v1 = self._sub_records[idx].get_value(field.get_id())
                v2 = other_field_value._sub_records[idx].get_value(field.get_id())
                if v1.different_to(v2):
                    return True
        return False
