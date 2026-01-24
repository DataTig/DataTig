import json

from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeStaticSiteFullCalendarIO(BasePipe):

    def __init__(self, output_dir="/"):
        self.output_dir = output_dir

    def start_build(self, current_info: CurrentInfo) -> None:

        config = current_info.get_context("datatig")["config"]
        base_url = current_info.get_context("datatig")["base_url"]
        datastore = current_info.get_context("datatig")["datastore"]

        #  Calendar
        for calendar_id, calendar_config in config.get_calendars().items():

            fullcalendar: list = []
            for cal_event in datastore.get_calendar_events_in_calendar(calendar_id):
                fullcalendar.append(
                    {
                        "id": cal_event.get_id(),
                        "title": cal_event.get_summary(),
                        "start": cal_event.get_start_iso(),
                        "end": cal_event.get_end_iso(),
                        "url": base_url
                        + cal_event.get_url("/type/{{type_id}}/record/{{record_id}}"),
                    }
                )
            self.build_directory.write(
                self.output_dir + "/calendar/{}".format(calendar_id),
                "fullcalendar.json",
                json.dumps(fullcalendar, indent=2),
            )
