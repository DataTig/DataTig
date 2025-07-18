import zoneinfo

from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldTimeZoneConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "timezone"

    def get_json_schema(self) -> dict:
        return {
            "type": "string",
            "enum": sorted(zoneinfo.available_timezones()),
            "title": self._title,
            "description": self._description,
        }

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):
        v = FieldTimeZoneValueModel(field=self, record=record)
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


class FieldTimeZoneValueModel(FieldValueModel):
    def set_value(self, value):
        if value:
            if value in zoneinfo.available_timezones():
                self._value = value
            else:
                # TODO raise error https://github.com/DataTig/DataTig/issues/20
                self._value = "UTC"
        else:
            self._value = None

    def has_value(self) -> bool:
        return isinstance(self._value, str)

    def get_value(self):
        return self._value

    def get_frictionless_csv_data_values(self):
        return [self._value]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        return {"value": self._value}

    def get_urls_in_value(self) -> list:
        return [self._value] if self._value else []
