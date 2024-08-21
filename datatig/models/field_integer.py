from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldIntegerConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "integer"

    def get_json_schema(self) -> dict:
        return {
            "type": "integer",
            "title": self._title,
            "description": self._description,
        }

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):

        v = FieldIntegerValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": "integer",
            }
        ]


class FieldIntegerValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = None
        if isinstance(value, str):
            self._value = int(value)
        elif isinstance(value, int):
            self._value = value
        elif isinstance(value, float):
            self._value = int(value)

    def get_value(self):
        return self._value

    def get_frictionless_csv_data_values(self):
        return [self._value]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        return {"value": self._value}
