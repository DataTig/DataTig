import json

from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeStaticSiteAPI(BasePipe):

    def start_build(self, current_info: CurrentInfo) -> None:

        # Root

        config = current_info.get_context("datatig")["config"]
        base_url = current_info.get_context("datatig")["base_url"]

        api: dict = {
            "title": config.get_title(),
            "description": config.get_description(),
            "types": {},
            "calendars": {},
        }
        for type, type_config in config.get_types().items():
            api["types"][type] = {
                "id": type,
                "human_url": base_url + "/type/" + type + "/",
                "api_url": base_url + "/type/" + type + "/api.json",
            }
        for calendar_id, calendar_config in config.get_calendars().items():
            api["calendars"][calendar_id] = {
                "id": calendar_id,
                "human_url": base_url + "/calendar/" + calendar_id + "/",
                "api_url": base_url + "/calendar/" + calendar_id + "/api.json",
            }

        self.build_directory.write(
            "/",
            "api.json",
            json.dumps(api, indent=2),
        )

        # Type

        for type, type_config in config.get_types().items():

            api_type: dict = {
                "id": type,
                "fields": {},
                "records_api_url": base_url + "/type/" + type + "/records_api.json",
            }
            for field_name, field in type_config.get_fields().items():
                api_type["fields"][field_name] = {
                    "id": field_name,
                    "type": field.get_type(),
                }

            self.build_directory.write(
                "/type/{}".format(type),
                "api.json",
                json.dumps(api_type, indent=2),
            )
