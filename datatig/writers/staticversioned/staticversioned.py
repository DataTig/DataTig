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
from datatig.sqliteversioned import DataStoreSQLiteVersioned


class StaticVersionedWriter:
    def __init__(
        self,
        datastore: DataStoreSQLiteVersioned,
        out_dir: str,
        default_ref: str,
        url: Optional[str] = None,
    ):
        self._datastore: DataStoreSQLiteVersioned = datastore
        self._template_variables: dict = {}
        self._out_dir: str = out_dir
        self._url: str = url or ""
        self._default_ref: str = default_ref
        self._default_config: SiteConfigModel = datastore.get_config(default_ref)

    def go(self) -> None:
        # Templates
        jinja2_env = Environment(
            loader=FileSystemLoader(
                searchpath=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)), "templates"
                )
            ),
            autoescape=select_autoescape(["html", "xml"]),
        )

        self._template_variables = {
            "url": self._url,
            "datastore": self._datastore,
            "datastore_file_size_bytes": os.path.getsize(
                self._datastore.get_file_name()
            ),
            "git_commits_with_refs": self._datastore.get_git_refs(),
            "default_ref_str": self._default_ref,
            "default_config": self._default_config,
        }

        # Out Dir
        os.makedirs(self._out_dir, exist_ok=True)

        # Top Level Static Pages
        for page in ["robots.txt", "index.html"]:
            self._write_template("", page, page, {}, jinja2_env)

        # Assets
        assets_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        for filename in [
            f
            for f in os.listdir(assets_dir)
            if os.path.isfile(os.path.join(assets_dir, f))
        ]:
            name_bits = filename.split(".")
            if name_bits[-1] in ["css", "js"]:
                shutil.copy(
                    os.path.join(assets_dir, filename),
                    os.path.join(self._out_dir, filename),
                )

        # Asset - Pygments
        with open(os.path.join(self._out_dir, "pygments.css"), "w") as fp:
            fp.write(pygments.formatters.HtmlFormatter().get_style_defs(".highlight"))

        # Refs
        for git_commit in self._datastore.get_git_refs():
            self._go_ref(git_commit, jinja2_env)

        # Types
        for type in self._default_config.get_types().values():
            self._go_type(type, jinja2_env)

        # All Data
        shutil.copy(
            self._datastore.get_file_name(),
            os.path.join(self._out_dir, "database.sqlite"),
        )

    def _go_ref(
        self,
        git_commit,
        jinja2_env: Environment,
    ):
        # Index page
        if self._default_ref == git_commit.get_ref():
            self._write_template(
                os.path.join("ref", git_commit.get_ref()),
                "index.html",
                "ref/index.default.html",
                {"git_commit": git_commit},
                jinja2_env,
            )
        elif not self._datastore.is_config_same_between_refs(
            git_commit.get_commit_hash(), self._default_ref
        ):
            self._write_template(
                os.path.join("ref", git_commit.get_ref()),
                "index.html",
                "ref/index.configdifferent.html",
                {"git_commit": git_commit},
                jinja2_env,
            )
        else:
            self._write_template(
                os.path.join("ref", git_commit.get_ref()),
                "index.html",
                "ref/index.html",
                {
                    "git_commit": git_commit,
                    "data_differences_between_refs": self._datastore.get_data_differences_between_refs(
                        self._default_ref, git_commit.get_commit_hash()
                    ),
                    "errors_added_between_refs": self._datastore.get_errors_added_between_refs(
                        self._default_ref, git_commit.get_commit_hash()
                    ),
                },
                jinja2_env,
            )
        # Errors
        self._write_template(
            os.path.join("ref", git_commit.get_ref()),
            "errors.html",
            "ref/errors.html",
            {"git_commit": git_commit},
            jinja2_env,
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

        # Each Item/Record!
        for item_id in self._datastore.get_ids_in_type(
            self._default_ref, type.get_id()
        ):
            self._go_record(type, item_id, jinja2_env)

    def _go_record(self, type: TypeModel, record_id: str, jinja2_env: Environment):
        # vars
        record: RecordModel = self._datastore.get_item(
            self._default_ref, type.get_id(), record_id
        )
        item_template_vars: dict = {
            "type": type,
            "item": record,
            "refs": {},
        }
        item_template_vars["record_data_html"] = pygments.highlight(
            json.dumps(record.get_data(), indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )
        for git_commit in self._datastore.get_git_refs():
            if git_commit.get_ref() != self._default_ref:
                ref_data: dict = {
                    "exists": False,
                    "config_same": False,
                    "record": None,
                    "diff": None,
                    "record_errors_added": False,
                    "record_errors_removed": False,
                }
                if self._datastore.is_config_same_between_refs(
                    git_commit.get_ref(), self._default_ref
                ):
                    ref_data["config_same"] = True
                    ref_record: Optional[RecordModel] = self._datastore.get_item(
                        git_commit.get_ref(), type.get_id(), record_id
                    )
                    if ref_record:
                        ref_data["exists"] = True
                        ref_data["record"] = ref_record  # type: ignore
                        ref_data["diff"] = ref_record.get_diff(record)  # type: ignore
                        ref_data[
                            "record_errors_added"
                        ] = self._datastore.get_record_errors_added_between_refs_for_record(
                            self._default_ref,
                            git_commit.get_ref(),
                            type.get_id(),
                            record_id,
                        )
                        ref_data[
                            "record_errors_removed"
                        ] = self._datastore.get_record_errors_removed_between_refs_for_record(
                            self._default_ref,
                            git_commit.get_ref(),
                            type.get_id(),
                            record_id,
                        )
                item_template_vars["refs"][git_commit.get_ref()] = ref_data
        # pages
        self._write_template(
            os.path.join("type", type.get_id(), "record", record_id),
            "index.html",
            "type/record/index.html",
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
