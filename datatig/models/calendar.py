import pytz

from datatig.exceptions import SiteConfigurationException
from datatig.models.calendar_data import CalendarDataModel


class CalendarModel:
    def __init__(self, siteconfig):
        self._id = None
        self._datas = []
        self._timezone = "UTC"
        self._siteconfig = siteconfig

    def load_from_config(self, id: str, config: dict) -> None:
        self._id = id
        datas = config.get("datas", [])
        if isinstance(datas, dict):
            datas = [datas]
        for data_config in datas:
            calendar_data = CalendarDataModel(self._siteconfig)
            calendar_data.load_from_config(data_config)
            self._datas.append(calendar_data)
        self._timezone = config.get("timezone", "UTC")
        if self._timezone != "UTC":
            try:
                pytz.timezone(self._timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                raise SiteConfigurationException(
                    "Calendar {} has unknown timezone {}".format(
                        self._id, self._timezone
                    )
                )

    def get_id(self) -> str:
        return self._id

    def get_datas(self) -> list:
        return self._datas

    def get_timezone(self) -> str:
        return self._timezone
