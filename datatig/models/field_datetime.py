import datetime
import zoneinfo
from typing import Optional

import dateparser

from datatig.exceptions import SiteConfigurationException
from datatig.jsondeepreaderwriter import JSONDeepReaderWriter
from datatig.models.field import FieldConfigModel, FieldValueModel


class FieldDateTimeConfigModel(FieldConfigModel):
    def get_type(self) -> str:
        return "datetime"

    def _load_extra_config(self, config: dict) -> None:
        self._extra_config["timezone"] = config.get("timezone", "UTC")
        if (
            self._extra_config["timezone"] != "UTC"
            and not self._extra_config["timezone"] in zoneinfo.available_timezones()
        ):
            raise SiteConfigurationException(
                "DateTime field {} has unknown timezone {}".format(
                    self._id, self._extra_config["timezone"]
                )
            )

    def get_json_schema(self) -> dict:
        return {
            "type": "string",
            "format": "date-time",
            "title": self._title,
            "description": self._description,
        }

    def get_new_item_json(self):
        return None

    def get_value_object(self, record, data):

        v = FieldDateTimeValueModel(field=self, record=record)
        obj = JSONDeepReaderWriter(data)
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

    def get_timezone(self) -> str:
        return self.get_extra_config().get("timezone", "UTC")


class FieldDateTimeValueModel(FieldValueModel):
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
        elif isinstance(value, datetime.datetime):
            self._value = value.replace(
                tzinfo=zoneinfo.ZoneInfo(self._field.get_timezone())
            )
        elif isinstance(value, datetime.date):
            self._value = datetime.datetime(
                value.year,
                value.month,
                value.day,
                0,
                0,
                0,
                tzinfo=zoneinfo.ZoneInfo(self._field.get_timezone()),
            )

    def has_value(self) -> bool:
        return isinstance(self._value, datetime.datetime)

    def get_value_datetime_object(
        self,
        fallback_hour=0,
        fallback_min=0,
        fallback_sec=0,
    ) -> Optional[datetime.datetime]:
        # fallback options not used here as datetime already comes with them, but they are used in FieldDateValueModel
        # and we want the method signature to be the same
        # so that FieldDateValueModel and FieldDateTimeValueModel can be treated the same.
        return self._value

    def get_value(self):
        if self._value:
            return self._value.isoformat()
        else:
            return None

    def get_value_timestamp(self) -> Optional[float]:
        if self._value:
            return self._value.timestamp()
        else:
            return None

    def get_frictionless_csv_data_values(self):
        return [self.get_value(), self.get_value_timestamp()]

    def different_to(self, other_field_value):
        return self._value != other_field_value._value

    def get_api_value(self) -> dict:
        if self._value:
            return {
                "value_iso": self.get_value(),
                "value_timestamp": self.get_value_timestamp(),
            }
        else:
            return {"value_iso": None, "value_timestamp": None}
