from datatig.models.calendar_data import CalendarDataModel


class CalendarModel:
    def __init__(self):
        self._id = None
        self._datas = []

    def load_from_config(self, id: str, config: dict) -> None:
        self._id = id
        datas = config.get("datas", [])
        if isinstance(datas, dict):
            datas = [datas]
        for config in datas:
            calendar_data = CalendarDataModel()
            calendar_data.load_from_config(config)
            self._datas.append(calendar_data)

    def get_id(self) -> str:
        return self._id

    def get_datas(self) -> list:
        return self._datas
