import datetime

import dateparser

from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldDateTimeConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "datetime"

    def get_json_schema(self) -> dict:
        return {
            "type": "string",
            "format": "date-time",
            "title": self._title,
        }

    def get_new_item_json(self):
        return None

    def get_value_object_from_record(self, record):
        v = FieldDateTimeValueModel(record=record, field_id=self._id)
        obj = JSONDeepReaderWriter(record.get_data())
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": "datetime",
            },
            {
                "name": "field_" + self.get_id() + "___timestamp",
                "title": self.get_title() + " (Timestamp)",
                "type": "integer",
            },
        ]


class FieldDateTimeValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = None
        if isinstance(value, str):
            self._value = dateparser.parse(value, settings={"TIMEZONE": "UTC"})
        elif isinstance(value, datetime.datetime):
            self._value = value

    def get_value(self):
        if self._value:
            return self._value.isoformat()
        else:
            return None

    def get_value_timestamp(self):
        if self._value:
            return self._value.replace(tzinfo=datetime.timezone.utc).timestamp()
        else:
            return None

    def get_frictionless_csv_data_values(self):
        return [self.get_value(), self.get_value_timestamp()]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value
