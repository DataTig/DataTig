import json
import os
import shutil
from typing import Optional

import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers.data  # type: ignore
from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
from spreadsheetforms.api import put_data_in_form  # type: ignore

from datatig.models.record import RecordModel
from datatig.models.type import TypeModel
from datatig.siteconfig import SiteConfig
from datatig.sqlite import DataStoreSQLite

from .static_util import jinja2_escapejs_filter


class StaticWriter:
    def __init__(
        self,
        config: SiteConfig,
        datastore: DataStoreSQLite,
        out_dir: str,
        url: Optional[str] = None,
    ):
        self.config = config
        self.datastore = datastore
        self._template_variables: dict = {}
        self.out_dir = out_dir
        self._url: str = url or ""

    def go(self) -> None:
        # Templates
        jinja2_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "statictemplates"
                )
            ),
            autoescape=select_autoescape(["html", "xml"]),
        )
        jinja2_env.filters["escapejs"] = jinja2_escapejs_filter

        self._template_variables = {
            "site_title": self.config.config.get("title", "SITE"),
            "site_description": self.config.config.get("description", ""),
            "site_github_url": self.config.github_url(),
            "site_githost_primary_branch": self.config.githost_primary_branch(),
            "types": {},
            "datastore": self.datastore,
            "url": self._url,
        }

        for k, v in self.config.types.items():
            self._template_variables["types"][k] = {
                "id": k,
                "fields": v.fields,
                "list_fields": v.list_fields(),
                "directory": v.directory(),
                "directory_in_git_repository": v.directory_in_git_repository(),
                "guide_form_xlsx": v.guide_form_xlsx(),
                "pretty_json_indent": v.pretty_json_indent(),
                "default_format": v.default_format(),
                "markdown_body_is_field": v.markdown_body_is_field(),
                "json_schema_string": json.dumps(v.json_schema_as_dict()),
            }

        # Out Dir
        os.makedirs(self.out_dir, exist_ok=True)

        # Top Level Static Pages
        for page in ["robots.txt", "index.html", "errors.html"]:
            self._write_template("", page, page, {}, jinja2_env)

        # API
        api: dict = {
            "title": self.config.config.get("title", "SITE"),
            "description": self.config.config.get("description", ""),
            "types": {},
        }
        for type, type_config in self.config.types.items():
            api["types"][type] = {
                "id": type,
                "human_url": self._url + "/type/" + type + "/",
                "api_url": self._url + "/type/" + type + "/api.json",
            }
        with open(os.path.join(self.out_dir, "api.json"), "w") as fp:
            json.dump(api, fp, indent=2)

        # Assets
        assets_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "staticassets"
        )
        for filename in [
            f
            for f in os.listdir(assets_dir)
            if os.path.isfile(os.path.join(assets_dir, f))
        ]:
            name_bits = filename.split(".")
            if name_bits[-1] in ["css", "js"]:
                shutil.copy(
                    os.path.join(assets_dir, filename),
                    os.path.join(self.out_dir, filename),
                )

        # Asset - Pygments
        with open(os.path.join(self.out_dir, "pygments.css"), "w") as fp:
            fp.write(pygments.formatters.HtmlFormatter().get_style_defs(".highlight"))

        # Each Type!
        for type in self.config.types.values():
            self._go_type(type, jinja2_env)

        # All Data
        shutil.copy(
            self.datastore.get_file_name(),
            os.path.join(self.out_dir, "database.sqlite"),
        )

    def _go_type(self, type: TypeModel, jinja2_env: Environment):
        # pages
        self._write_template(
            os.path.join("type", type.id),
            "index.html",
            "type/index.html",
            {"type": self._template_variables["types"][type.id]},
            jinja2_env,
        )
        self._write_template(
            os.path.join("type", type.id, "newweb"),
            "index.html",
            "type/newweb.html",
            {"type": self._template_variables["types"][type.id]},
            jinja2_env,
        )

        # API
        api: dict = {
            "id": type.id,
            "fields": {},
            "records_api_url": self._url + "/type/" + type.id + "/records_api.json",
        }
        for field_name, field in type.fields.items():
            api["fields"][field_name] = {"id": field_name, "type": field.type()}
        with open(os.path.join(self.out_dir, "type", type.id, "api.json"), "w") as fp:
            json.dump(api, fp, indent=2)

        api_records: dict = {"records": {}}
        for item_id in self.datastore.get_ids_in_type(type.id):
            api_records["records"][item_id] = {
                "id": item_id,
                "api_url": self._url
                + "/type/"
                + type.id
                + "/record/"
                + item_id
                + "/api.json",
                "data_api_url": self._url
                + "/type/"
                + type.id
                + "/record/"
                + item_id
                + "/data.json",
            }
        with open(
            os.path.join(self.out_dir, "type", type.id, "records_api.json"), "w"
        ) as fp:
            json.dump(api_records, fp, indent=2)

        # Each Item/Record!
        for item_id in self.datastore.get_ids_in_type(type.id):
            self._go_record(type, item_id, jinja2_env)

    def _go_record(self, type: TypeModel, record_id: str, jinja2_env: Environment):
        # vars
        record: RecordModel = self.datastore.get_item(type.id, record_id)
        item_template_vars = {
            "type": self._template_variables["types"][type.id],
            "item_id": record_id,
            "item_data": record,
            "item_data_json_string": json.dumps(record.data),
        }
        item_template_vars["record_data_html"] = pygments.highlight(
            json.dumps(item_template_vars["item_data"].data, indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )
        # pages
        self._write_template(
            os.path.join("type", type.id, "record", record_id),
            "index.html",
            "type/record/index.html",
            item_template_vars,
            jinja2_env,
        )
        self._write_template(
            os.path.join("type", type.id, "record", record_id, "editweb"),
            "index.html",
            "type/record/editweb.html",
            item_template_vars,
            jinja2_env,
        )
        if type.guide_form_xlsx():
            self._write_template(
                os.path.join("type", type.id, "record", record_id, "editspreadsheet"),
                "index.html",
                "type/record/editspreadsheet.html",
                item_template_vars,
                jinja2_env,
            )
        # data files
        with open(
            os.path.join(
                self.out_dir,
                "type",
                type.id,
                "record",
                record_id,
                "data.json",
            ),
            "w",
        ) as fp:
            json.dump(record.data, fp, indent=2)
        if type.guide_form_xlsx():
            out_form_xlsx = os.path.join(
                self.out_dir,
                "type",
                type.id,
                "record",
                record_id,
                "data-form.xlsx",
            )
            put_data_in_form(
                os.path.join(self.config.source_dir, type.guide_form_xlsx()),
                record.data,
                out_form_xlsx,
            )
        # API
        api: dict = {
            "data_api_url": self._url
            + "/type/"
            + type.id
            + "/record/"
            + record_id
            + "/data.json",
        }
        with open(
            os.path.join(
                self.out_dir, "type", type.id, "record", record_id, "api.json"
            ),
            "w",
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
        os.makedirs(os.path.join(self.out_dir, dirname), exist_ok=True)
        variables.update(self._template_variables)
        with open(os.path.join(self.out_dir, dirname, filename), "w") as fp:
            fp.write(jinja2_env.get_template(templatename).render(**variables))
