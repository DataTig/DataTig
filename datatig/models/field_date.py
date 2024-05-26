import datetime
from typing import Optional

import dateparser
import pytz

from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldDateConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "date"

    def _load_extra_config(self, config: dict) -> None:
        self._extra_config["timezone"] = config.get("timezone", "UTC")
        if self._extra_config["timezone"] != "UTC":
            try:
                pytz.timezone(self._extra_config["timezone"])
            except pytz.exceptions.UnknownTimeZoneError:
                # TODO: Log somewhere that we have done this
                self._extra_config["timezone"] = "UTC"

    def get_json_schema(self) -> dict:
        return {
            "type": "string",
            "format": "date",
            "title": self._title,
        }

    def get_new_item_json(self):
        return None

    def get_value_object_from_record(self, record):
        v = FieldDateValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(record.get_data())
        v.set_value(obj.read(self._key))
        return v

    def get_frictionless_csv_field_specifications(self):
        return [
            {
                "name": "field_" + self.get_id(),
                "title": self.get_title(),
                "type": "date",
            },
            {
                "name": "field_" + self.get_id() + "___timestamp",
                "title": self.get_title() + " (Timestamp)",
                "type": "integer",
            },
        ]

    def get_timezone(self) -> str:
        return self.get_extra_config().get("timezone", "UTC")


class FieldDateValueModel(FieldValueModel):
    def set_value(self, value):
        self._value = None
        if isinstance(value, str):
            self._value = dateparser.parse(
                value,
                settings={
                    "TIMEZONE": self._field.get_timezone(),
                    "RETURN_AS_TIMEZONE_AWARE": True,
                },
            )
            if self._value:
                self._value = self._value.date()
        elif isinstance(value, datetime.date):
            self._value = value
        elif isinstance(value, datetime.datetime):
            self._value = value.date()

    def get_value_datetime_object(self) -> Optional[datetime.datetime]:
        if self._value:
            timezone = self._field.get_timezone()  # type: ignore
            dt = datetime.datetime(
                self._value.year,
                self._value.month,
                self._value.day,
                12,
                0,
                0,
                0,
            )
            return pytz.timezone(timezone).localize(dt)
        else:
            return None

    def get_value(self):
        if self._value:
            return self._value.isoformat()
        else:
            return None

    def get_value_timestamp(self) -> Optional[float]:
        if self._value:
            timezone = self._field.get_timezone()  # type: ignore
            dt = datetime.datetime(
                self._value.year,
                self._value.month,
                self._value.day,
                0,
                0,
                0,
                0,
            )
            return pytz.timezone(timezone).localize(dt).timestamp()
        else:
            return None

    def get_frictionless_csv_data_values(self):
        return [self.get_value(), self.get_value_timestamp()]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value
