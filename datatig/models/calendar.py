import pytz

from datatig.models.calendar_data import CalendarDataModel


class CalendarModel:
    def __init__(self):
        self._id = None
        self._datas = []
        self._timezone = "UTC"

    def load_from_config(self, id: str, config: dict) -> None:
        self._id = id
        datas = config.get("datas", [])
        if isinstance(datas, dict):
            datas = [datas]
        for data_config in datas:
            calendar_data = CalendarDataModel()
            calendar_data.load_from_config(data_config)
            self._datas.append(calendar_data)
        self._timezone = config.get("timezone", "UTC")
        if self._timezone != "UTC":
            try:
                pytz.timezone(self._timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                # TODO: Log somewhere that we have done this
                self._timezone = "UTC"

    def get_id(self) -> str:
        return self._id

    def get_datas(self) -> list:
        return self._datas

    def get_timezone(self) -> str:
        return self._timezone
