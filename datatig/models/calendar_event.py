import datetime
from typing import Optional

from datatig.models.calendar_data import CalendarDataModel

from .record import RecordModel


class CalendarEventModel:
    def __init__(self):
        self._calendar_id: str = ""
        self._id: str = ""
        self._summary: str = ""
        self._start: datetime.datetime = None
        self._end: datetime.datetime = None
        self._type_id: str = ""
        self._record_id: str = ""

    def load_from_calendar_data_and_item(
        self, calendar_data: CalendarDataModel, record: RecordModel
    ) -> bool:
        # id
        self._id = (
            calendar_data.get_id_template()
            .replace("{{record_id}}", record.get_id())
            .replace("{{type_id}}", record.get_type().get_id())
        )
        # summary
        self._summary = record.get_field_value(
            calendar_data.get_summary_field()
        ).get_value()
        # start
        start_field_value = record.get_field_value(calendar_data.get_start_field())
        if not start_field_value:
            return False
        self._start = start_field_value.get_value_datetime_object()
        if not self._start:
            return False
        # end
        end_field_value = record.get_field_value(calendar_data.get_end_field())
        self._end = (
            end_field_value.get_value_datetime_object(
                fallback_hour=23, fallback_min=59, fallback_sec=59
            )
            if end_field_value
            else None
        ) or self._start
        # Success!
        return True

    def load_from_database(self, data: dict) -> None:
        self._calendar_id = data["calendar_id"]
        self._id = data["id"]
        self._summary = data["summary"]
        self._start = datetime.datetime.fromisoformat(data["start_iso"])
        self._end = datetime.datetime.fromisoformat(data["end_iso"])
        for k in data.keys():
            if k.startswith("record_") and data[k]:
                self._type_id = k[7:-5]
                self._record_id = data[k]

    def get_calendar_id(self) -> str:
        return self._calendar_id

    def get_id(self) -> str:
        return self._id

    def get_summary(self) -> str:
        return self._summary

    def get_start_datetime_object(self) -> datetime.datetime:
        return self._start

    def get_start_iso(self) -> str:
        return self._start.isoformat()

    def get_start_timestamp(self) -> float:
        return self._start.timestamp()

    def get_end_datetime_object(self) -> datetime.datetime:
        return self._end

    def get_end_iso(self) -> str:
        return self._end.isoformat()

    def get_end_timestamp(self) -> Optional[float]:
        return self._end.timestamp()

    def get_url(self, url: str) -> str:
        return url.replace("{{type_id}}", self._type_id).replace(
            "{{record_id}}", self._record_id
        )
