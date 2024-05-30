from datatig.exceptions import SiteConfigurationException


class CalendarDataModel:
    def __init__(self, siteconfig):
        self._type = None
        self._start_field: str = "start"
        self._end_field: str = "end"
        self._summary_field: str = "Summary"
        self._id_template: str = "{{type_id}}_{{record_id}}@example.com"
        self._siteconfig = siteconfig

    def load_from_config(self, config) -> None:
        # Type
        self._type = config.get("type")
        type = self._siteconfig.get_type(config.get("type"))
        if not type:
            raise SiteConfigurationException(
                "Calendar uses an unknown type {}".format(config.get("type"))
            )
        # Start
        self._start_field = config.get("start", self._start_field)
        if not type.get_field(self._start_field):
            raise SiteConfigurationException(
                "Calendar uses an unknown start field {} in type {}".format(
                    self._start_field, config.get("type")
                )
            )
        # End
        self._end_field = config.get("end", self._end_field)
        if not type.get_field(self._end_field):
            raise SiteConfigurationException(
                "Calendar uses an unknown end field {} in type {}".format(
                    self._end_field, config.get("type")
                )
            )
        # Summary
        self._summary_field = config.get("summary", self._summary_field)
        if not type.get_field(self._summary_field):
            raise SiteConfigurationException(
                "Calendar uses an unknown summary field {} in type {}".format(
                    self._summary_field, config.get("type")
                )
            )

        # Id
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
