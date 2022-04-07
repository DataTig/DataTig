from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldBooleanConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "boolean"

    def get_json_schema(self) -> dict:
        return {
            "type": "boolean",
            "title": self._title,
        }

    def get_new_item_json(self):
        return None

    def get_value_object_from_record(self, record):
        v = FieldBooleanValueModel(record=record, field_id=self._id)
        obj = JSONDeepReaderWriter(record.get_data())
        v.set_value(obj.read(self._key))
        return v


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

    def get_value(self):
        return self._value

    def is_value_true(self):
        return isinstance(self._value, bool) and self._value

    def is_value_false(self):
        return isinstance(self._value, bool) and not self._value
