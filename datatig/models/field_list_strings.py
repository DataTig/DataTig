from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldListStringsConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "list-strings"

    def get_json_schema(self) -> dict:
        out: dict = {
            "title": self._title,
            "description": self._description,
            "type": "array",
            "items": {"type": "string"},
            "uniqueItems": self._extra_config["unique_items"],
        }
        if self._required:
            out["minLength"] = 1
            if self._extra_config["string_min_length"]:
                out["items"]["minLength"] = max(
                    1, self._extra_config["string_min_length"]
                )
            else:
                out["items"]["minLength"] = 1
        elif self._extra_config["string_min_length"]:
            out["items"]["minLength"] = self._extra_config["string_min_length"]
        if self._extra_config["string_max_length"]:
            out["items"]["maxLength"] = self._extra_config["string_max_length"]
        return out

    def _load_extra_config(self, config: dict) -> None:
        self._extra_config["unique_items"] = config.get("unique_items", False)
        self._extra_config["string_min_length"] = (
            int(config.get("string_min_length", 0)) or None
        )
        self._extra_config["string_max_length"] = (
            int(config.get("string_max_length", 0)) or None
        )

    def get_new_item_json(self):
        return []

    def get_value_object(self, record, data):
        v = FieldListStringsValueModel(field=self, record=record)
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

    def has_value(self) -> bool:
        return len(self._value) > 0

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

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        return {"values": [{"value": i} for i in self._value]}
