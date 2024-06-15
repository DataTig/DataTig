import datetime
import re
from typing import Optional

import dateparser
import pytz

from datatig.exceptions import SiteConfigurationException
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
                raise SiteConfigurationException(
                    "Date field {} has unknown timezone {}".format(
                        self._id, self._extra_config["timezone"]
                    )
                )

    def get_json_schema(self) -> dict:
        return {
            "type": "string",
            "format": "date",
            "title": self._title,
            "description": self._description,
        }

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):
        v = FieldDateValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
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
            # dateparser can be very slow, so if it's a simple format we'll do it by regex
            m = re.search("([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])", value)
            if m:
                try:
                    self._value = datetime.date(
                        int(m.group(1)), int(m.group(2)), int(m.group(3))
                    )
                except ValueError:
                    self._value = None
            # Fall back to dateparser
            if not self._value:
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

    def get_value_datetime_object(
        self,
        fallback_hour=0,
        fallback_min=0,
        fallback_sec=0,
    ) -> Optional[datetime.datetime]:
        if self._value:
            timezone = self._field.get_timezone()  # type: ignore
            dt = datetime.datetime(
                self._value.year,
                self._value.month,
                self._value.day,
                fallback_hour,
                fallback_min,
                fallback_sec,
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
