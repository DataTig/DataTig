import json
import os
import shutil
from typing import Optional

import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers.data  # type: ignore
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore

from datatig.models.record import RecordModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.sqlite import DataStoreSQLite
from datatig.writers.frictionless.frictionless import FrictionlessWriter

from .static_util import jinja2_escapejs_filter


class StaticWriter:
    def __init__(
        self,
        config: SiteConfigModel,
        datastore: DataStoreSQLite,
        out_dir: str,
        url: Optional[str] = None,
    ):
        self._config: SiteConfigModel = config
        self._datastore: DataStoreSQLite = datastore
        self._template_variables: dict = {}
        self._out_dir: str = out_dir
        self._url: str = url or ""

    def go(self) -> None:
        # Templates
        jinja2_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "..",
                    "..",
                    "templates",
                    "static",
                )
            ),
            autoescape=select_autoescape(["html", "xml"]),
        )
        jinja2_env.filters["escapejs"] = jinja2_escapejs_filter

        self._template_variables = {
            "site": self._config,
            "url": self._url,
            "datastore": self._datastore,
            "datastore_file_size_bytes": os.path.getsize(
                self._datastore.get_file_name()
            ),
        }

        # Out Dir
        os.makedirs(self._out_dir, exist_ok=True)

        # Frictionless
        frictionless_writer = FrictionlessWriter(
            self._config,
            self._datastore,
            os.path.join(self._out_dir, "frictionless.zip"),
        )
        frictionless_writer.go()
        self._template_variables["frictionless_file_size_bytes"] = os.path.getsize(
            os.path.join(self._out_dir, "frictionless.zip")
        )

        # Top Level Static Pages
        for page in ["robots.txt", "index.html", "errors.html"]:
            self._write_template("", page, page, {}, jinja2_env)

        # API
        api: dict = {
            "title": self._config.get_title(),
            "description": self._config.get_description(),
            "types": {},
            "calendars": {},
        }
        for type, type_config in self._config.get_types().items():
            api["types"][type] = {
                "id": type,
                "human_url": self._url + "/type/" + type + "/",
                "api_url": self._url + "/type/" + type + "/api.json",
            }
        for calendar_id, calendar_config in self._config.get_calendars().items():
            api["calendars"][calendar_id] = {
                "id": calendar_id,
                "human_url": self._url + "/calendar/" + calendar_id + "/",
                "api_url": self._url + "/calendar/" + calendar_id + "/api.json",
            }
        with open(os.path.join(self._out_dir, "api.json"), "w") as fp:
            json.dump(api, fp, indent=2)

        # Assets
        self._copy_assets(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "..",
                "assets",
                "all",
            ),
            self._out_dir,
        )
        self._copy_assets(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "..",
                "..",
                "assets",
                "static",
            ),
            self._out_dir,
        )

        # Asset - Pygments
        with open(os.path.join(self._out_dir, "pygments.css"), "w") as fp:
            fp.write(pygments.formatters.HtmlFormatter().get_style_defs(".highlight"))

        # Each Type!
        for type in self._config.get_types().values():
            self._go_type(type, jinja2_env)

        # Calendars
        for calendar_id, calendar_config in self._config.get_calendars().items():
            self._go_calendar(calendar_id, calendar_config, jinja2_env)

        # All Data
        shutil.copy(
            self._datastore.get_file_name(),
            os.path.join(self._out_dir, "database.sqlite"),
        )

    def _copy_assets(self, assets_dir: str, out_dir: str):
        os.makedirs(out_dir, exist_ok=True)
        for filename in os.listdir(assets_dir):
            if os.path.isfile(os.path.join(assets_dir, filename)):
                name_bits = filename.split(".")
                if name_bits[-1] in ["css", "js", "png", "txt", "ttf", "woff2"]:
                    shutil.copy(
                        os.path.join(assets_dir, filename),
                        os.path.join(out_dir, filename),
                    )
            elif os.path.isdir(os.path.join(assets_dir, filename)):
                self._copy_assets(
                    os.path.join(assets_dir, filename),
                    os.path.join(out_dir, filename),
                )

    def _go_type(self, type: TypeModel, jinja2_env: Environment):
        # pages
        self._write_template(
            os.path.join("type", type.get_id()),
            "index.html",
            "type/index.html",
            {"type": type},
            jinja2_env,
        )
        self._write_template(
            os.path.join("type", type.get_id(), "newweb"),
            "index.html",
            "type/newweb.html",
            {"type": type},
            jinja2_env,
        )

        # API
        api: dict = {
            "id": type.get_id(),
            "fields": {},
            "records_api_url": self._url
            + "/type/"
            + type.get_id()
            + "/records_api.json",
        }
        for field_name, field in type.get_fields().items():
            api["fields"][field_name] = {"id": field_name, "type": field.get_type()}
        with open(
            os.path.join(self._out_dir, "type", type.get_id(), "api.json"), "w"
        ) as fp:
            json.dump(api, fp, indent=2)

        api_records: dict = {"records": {}}
        for item_id in self._datastore.get_ids_in_type(type.get_id()):
            item = self._datastore.get_item(type.get_id(), item_id)
            api_records["records"][item_id] = {
                "id": item_id,
                "api_url": self._url
                + "/type/"
                + type.get_id()
                + "/record/"
                + item_id
                + "/api.json",
                "data_api_url": self._url
                + "/type/"
                + type.get_id()
                + "/record/"
                + item_id
                + "/data.json",
                "fields": {},
            }
            for field_id in type.get_list_fields():
                api_records["records"][item_id]["fields"][
                    field_id
                ] = item.get_field_value(field_id).get_api_value()
        with open(
            os.path.join(self._out_dir, "type", type.get_id(), "records_api.json"), "w"
        ) as fp:
            json.dump(api_records, fp, indent=2)

        # Each Item/Record!
        for item_id in self._datastore.get_ids_in_type(type.get_id()):
            self._go_record(type, item_id, jinja2_env)

    def _go_record(self, type: TypeModel, record_id: str, jinja2_env: Environment):
        # vars
        record: RecordModel = self._datastore.get_item(type.get_id(), record_id)
        item_template_vars = {
            "type": type,
            "item": record,
            "calendar_events": self._datastore.get_calendar_events_in_record(record),
        }
        item_template_vars["calendar_ids"] = list(
            set([i.get_calendar_id() for i in item_template_vars["calendar_events"]])  # type: ignore
        )
        item_template_vars["record_data_html"] = pygments.highlight(
            json.dumps(record.get_data(), indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )
        # pages
        self._write_template(
            os.path.join("type", type.get_id(), "record", record_id),
            "index.html",
            "type/record/index.html",
            item_template_vars,
            jinja2_env,
        )
        self._write_template(
            os.path.join("type", type.get_id(), "record", record_id, "editweb"),
            "index.html",
            "type/record/editweb.html",
            item_template_vars,
            jinja2_env,
        )
        # data files
        with open(
            os.path.join(
                self._out_dir,
                "type",
                type.get_id(),
                "record",
                record_id,
                "data.json",
            ),
            "w",
        ) as fp:
            json.dump(record.get_data(), fp, indent=2)
        # API
        api: dict = {
            "data_api_url": self._url
            + "/type/"
            + type.get_id()
            + "/record/"
            + record_id
            + "/data.json",
            "fields": {},
        }
        for field_id in type.get_fields().keys():
            api["fields"][field_id] = record.get_field_value(field_id).get_api_value()
        with open(
            os.path.join(
                self._out_dir, "type", type.get_id(), "record", record_id, "api.json"
            ),
            "w",
        ) as fp:
            json.dump(api, fp, indent=2)

    def _go_calendar(self, calendar_id: str, calendar_config, jinja2_env: Environment):
        # Index page
        self._write_template(
            os.path.join("calendar", calendar_id),
            "index.html",
            "calendar/index.html",
            {"calendar": calendar_config},
            jinja2_env,
        )

        # Fullcalendar.io data
        fullcalendar: list = []
        for cal_event in self._datastore.get_calendar_events_in_calendar(calendar_id):
            fullcalendar.append(
                {
                    "id": cal_event.get_id(),
                    "title": cal_event.get_summary(),
                    "start": cal_event.get_start_iso(),
                    "end": cal_event.get_end_iso(),
                    "url": self._url
                    + cal_event.get_url("/type/{{type_id}}/record/{{record_id}}"),
                }
            )
        with open(
            os.path.join(self._out_dir, "calendar", calendar_id, "fullcalendar.json"),
            "w",
        ) as fp:
            json.dump(fullcalendar, fp, indent=2)

        # API
        api: dict = {
            "id": calendar_id,
        }
        with open(
            os.path.join(self._out_dir, "calendar", calendar_id, "api.json"), "w"
        ) as fp:
            json.dump(api, fp, indent=2)

    def _write_template(
        self,
        dirname: str,
        filename: str,
        templatename: str,
        variables: dict,
        jinja2_env: Environment,
    ) -> None:
        os.makedirs(os.path.join(self._out_dir, dirname), exist_ok=True)
        variables.update(self._template_variables)
        with open(os.path.join(self._out_dir, dirname, filename), "w") as fp:
            fp.write(jinja2_env.get_template(templatename).render(**variables))
