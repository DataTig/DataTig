from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldURLConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "url"

    def get_json_schema(self) -> dict:
        return {
            "type": "string",
            "format": "uri",
            "title": self._title,
            "description": self._description,
        }

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):

        v = FieldURLValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": "string",
                "format": "uri",
            }
        ]


class FieldURLValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_frictionless_csv_data_values(self):
        return [self._value]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value
