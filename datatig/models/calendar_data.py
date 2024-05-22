class CalendarDataModel:
    def __init__(self):
        self._type = None
        self._start_field: str = "start"
        self._end_field: str = "end"
        self._summary_field: str = "Summary"
        self._id_template: str = "{{type_id}}_{{record_id}}@example.com"

    def load_from_config(self, config) -> None:
        self._type = config.get("type")
        self._start_field = config.get("start", self._start_field)
        self._end_field = config.get("end", self._end_field)
        self._summary_field = config.get("summary", self._summary_field)
        self._id_template = config.get("id", self._id_template)

    def get_type_id(self) -> str:
        return self._type

    def get_summary_field(self) -> str:
        return self._summary_field

    def get_start_field(self) -> str:
        return self._start_field

    def get_end_field(self) -> str:
        return self._end_field

    def get_id_template(self) -> str:
        return self._id_template
