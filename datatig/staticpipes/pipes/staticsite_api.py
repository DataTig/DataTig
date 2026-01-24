import json

from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeStaticSiteAPI(BasePipe):

    def start_build(self, current_info: CurrentInfo) -> None:

        # Root

        config = current_info.get_context("datatig")["config"]
        base_url = current_info.get_context("datatig")["base_url"]
        datastore = current_info.get_context("datatig")["datastore"]

        api: dict = {
            "title": config.get_title(),
            "description": config.get_description(),
            "types": {},
            "calendars": {},
        }
        for type_id, type_config in config.get_types().items():
            api["types"][type_id] = {
                "id": type_id,
                "human_url": base_url + "/type/" + type_id + "/",
                "api_url": base_url + "/type/" + type_id + "/api.json",
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

        for type_id, type_config in config.get_types().items():

            api_type: dict = {
                "id": type_id,
                "fields": {},
                "records_api_url": base_url + "/type/" + type_id + "/records_api.json",
            }
            for field_name, field in type_config.get_fields().items():
                api_type["fields"][field_name] = {
                    "id": field_name,
                    "type": field.get_type(),
                }

            self.build_directory.write(
                "/type/{}".format(type_id),
                "api.json",
                json.dumps(api_type, indent=2),
            )

            api_type_records: dict = {"records": {}}
            for item_id in datastore.get_ids_in_type(type_id):
                item = datastore.get_item(type_id, item_id)
                api_type_records["records"][item_id] = {
                    "id": item_id,
                    "api_url": base_url
                    + "/type/"
                    + type_id
                    + "/record/"
                    + item_id
                    + "/api.json",
                    "data_api_url": base_url
                    + "/type/"
                    + type_id
                    + "/record/"
                    + item_id
                    + "/data.json",
                    "fields": {},
                }
                for field_id in type_config.get_list_fields():
                    api_type_records["records"][item_id]["fields"][field_id] = (
                        item.get_field_value(field_id).get_api_value()
                    )

            self.build_directory.write(
                "/type/{}".format(type_id),
                "records_api.json",
                json.dumps(api_type_records, indent=2),
            )

        #  Calendar
        for calendar_id, calendar_config in config.get_calendars().items():
            api_calendar: dict = {
                "id": calendar_id,
            }
            self.build_directory.write(
                "/calendar/{}".format(calendar_id),
                "api.json",
                json.dumps(api_calendar, indent=2),
            )
