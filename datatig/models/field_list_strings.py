from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldListStringsConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "list-strings"

    def get_json_schema(self) -> dict:
        return {"title": self._title, "type": "array", "items": {"type": "string"}}

    def get_new_item_json(self):
        return []

    def get_value_object_from_record(self, record):
        v = FieldListStringsValueModel(record=record, field_id=self._id)
        obj = JSONDeepReaderWriter(record.get_data())
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": "string",
            }
        ]

    def get_frictionless_csv_resource_specifications(self) -> list:
        return [
            {
                "name": "values",
                "fields": [
                    {"name": "value", "title": "Value", "type": "string"},
                ],
            }
        ]


class FieldListStringsValueModel(FieldValueModel):
    def set_value(self, value):
        if value is None:
            value = []
        if not isinstance(value, list):
            value = [value]
        self._value = value

    def get_value(self):
        return self._value

    def get_frictionless_csv_data_values(self):
        if isinstance(self._value, list):
            return [", ".join([str(i) for i in self._value])]
        else:
            return [self._value]

    def get_frictionless_csv_resource_data_values(self, resource_name: str) -> list:
        if isinstance(self._value, list):
            return [[str(i)] for i in self._value]
        else:
            return [[self._value]]
