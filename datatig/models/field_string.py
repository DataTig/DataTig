from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldStringConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "string"

    def _load_extra_config(self, config: dict) -> None:
        self._extra_config["multiline"] = bool(config.get("multiline", False))

    def get_json_schema(self) -> dict:
        out = {
            "type": "string",
            "title": self._title,
            "description": self._description,
        }
        if self._extra_config.get("multiline"):
            out["format"] = "textarea"
        return out

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):

        v = FieldStringValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
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


class FieldStringValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = str(value) if value is not None else None

    def get_value(self):
        return self._value

    def get_frictionless_csv_data_values(self):
        return [self._value]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        return {"value": self._value}
