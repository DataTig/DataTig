from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldBooleanConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "boolean"

    def get_json_schema(self) -> dict:
        return {
            "type": "boolean",
            "title": self._title,
            "description": self._description,
        }

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):

        v = FieldBooleanValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": " boolean",
            }
        ]


class FieldBooleanValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = None
        if isinstance(value, bool):
            self._value = value
        elif isinstance(value, str):
            first_char = value.strip().lower()[:1]
            if first_char in ["1", "t"]:
                self._value = True
            elif first_char in ["0", "f"]:
                self._value = False
        elif isinstance(value, int):
            self._value = value > 0

    def has_value(self) -> bool:
        return isinstance(self._value, bool)

    def get_value(self):
        return self._value

    def is_value_true(self):
        return isinstance(self._value, bool) and self._value

    def is_value_false(self):
        return isinstance(self._value, bool) and not self._value

    def get_frictionless_csv_data_values(self):
        if self.is_value_true():
            return ["true"]
        elif self.is_value_false():
            return ["false"]
        else:
            return [""]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        if self.is_value_true():
            return {"value": True}
        elif self.is_value_false():
            return {"value": False}
        else:
            return {"value": None}
