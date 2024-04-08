import datetime
from typing import Optional

from datatig.models.calendar_data import CalendarData

from .record import RecordModel


class CalendarEvent:
    def __init__(self):
        self._id: str = ""
        self._summary: str = ""
        self._start: Optional[datetime.datetime] = None
        self._end: Optional[datetime.datetime] = None

    def load_from_calendar_data_and_item(
        self, calendar_data: CalendarData, record: RecordModel
    ) -> None:
        # id
        self._id = (
            calendar_data.get_id_template()
            .replace("ID", record.get_id())
            .replace("TYPE", record.get_type().get_id())
        )
        # summary
        self._summary = record.get_field_value(
            calendar_data.get_summary_field()
        ).get_value()
        # start
        start_field_value = record.get_field_value(calendar_data.get_start_field())
        self._start = (
            start_field_value.get_value_datetime_object() if start_field_value else None
        )
        # end
        end_field_value = record.get_field_value(calendar_data.get_end_field())
        self._end = (
            end_field_value.get_value_datetime_object() if end_field_value else None
        ) or self._start

    def get_id(self) -> str:
        return self._id

    def get_summary(self) -> str:
        return self._summary

    def get_start_iso(self) -> str:
        return self._start.isoformat() if self._start else ""

    def get_start_timestamp(self) -> Optional[float]:
        return (
            self._start.replace(tzinfo=datetime.timezone.utc).timestamp()
            if self._start
            else -1
        )

    def get_end_iso(self) -> str:
        return self._end.isoformat() if self._end else ""

    def get_end_timestamp(self) -> Optional[float]:
        return (
            self._end.replace(tzinfo=datetime.timezone.utc).timestamp()
            if self._end
            else -1
        )
