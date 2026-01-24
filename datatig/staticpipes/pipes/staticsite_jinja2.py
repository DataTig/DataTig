import json

import pygments
from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeStaticSiteJinja2(BasePipe):

    def __init__(self, jinja2_environment=None):
        self._jinja2_environment = jinja2_environment

    def start_build(self, current_info: CurrentInfo) -> None:

        actual_jinja2_environment = self._jinja2_environment.get(
            source_directory=self.source_directory,
            secondary_source_directories=self.secondary_source_directories,
        )
        config = current_info.get_context("datatig")["config"]
        # base_url = current_info.get_context("datatig")["base_url"]
        datastore = current_info.get_context("datatig")["datastore"]

        # Root pages
        for filename in ["index.html", "errors.html", "robots.txt"]:

            self.build_directory.write(
                "/",
                filename,
                actual_jinja2_environment.get_template(
                    "bundle_datatig_staticsite_templates:static/" + filename
                ).render(current_info.get_context()),
            )

        # For each type
        for type_id, type_config in config.get_types().items():

            context = current_info.get_context()
            context.update({"type": type_config})

            self.build_directory.write(
                "/type/{}".format(type_id),
                "index.html",
                actual_jinja2_environment.get_template(
                    "bundle_datatig_staticsite_templates:static/type/index.html"
                ).render(context),
            )

            self.build_directory.write(
                "/type/{}/newweb".format(type_id),
                "index.html",
                actual_jinja2_environment.get_template(
                    "bundle_datatig_staticsite_templates:static/type/newweb.html"
                ).render(context),
            )

            # For each item

            for item_id in datastore.get_ids_in_type(type_id):
                item = datastore.get_item(type_id, item_id)

                item_context = current_info.get_context()
                item_context.update(
                    {
                        "type": type_config,
                        "item": item,
                        "calendar_events": datastore.get_calendar_events_in_record(
                            item
                        ),
                    }
                )
                item_context["calendar_ids"] = list(
                    set([i.get_calendar_id() for i in item_context["calendar_events"]])  # type: ignore
                )
                item_context["record_data_html"] = pygments.highlight(
                    json.dumps(item.get_data(), indent=4),
                    pygments.lexers.data.JsonLexer(),
                    pygments.formatters.HtmlFormatter(),
                )

                self.build_directory.write(
                    "/type/{}/record/{}".format(type_id, item_id),
                    "index.html",
                    actual_jinja2_environment.get_template(
                        "bundle_datatig_staticsite_templates:static/type/record/index.html"
                    ).render(item_context),
                )

                self.build_directory.write(
                    "/type/{}/record/{}/editweb".format(type_id, item_id),
                    "index.html",
                    actual_jinja2_environment.get_template(
                        "bundle_datatig_staticsite_templates:static/type/record/editweb.html"
                    ).render(item_context),
                )

        # For each Calendar
        for calendar_id, calendar_config in config.get_calendars().items():
            context = current_info.get_context()
            context.update({"calendar": calendar_config})

            self.build_directory.write(
                "/calendar/{}".format(calendar_id),
                "index.html",
                actual_jinja2_environment.get_template(
                    "bundle_datatig_staticsite_templates:static/calendar/index.html"
                ).render(context),
            )
