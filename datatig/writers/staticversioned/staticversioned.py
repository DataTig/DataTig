import os
import shutil
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore

from datatig.sqliteversioned import DataStoreSQLiteVersioned


class StaticVersionedWriter:
    def __init__(
        self,
        datastore: DataStoreSQLiteVersioned,
        out_dir: str,
        url: Optional[str] = None,
    ):
        self._datastore: DataStoreSQLiteVersioned = datastore
        self._template_variables: dict = {}
        self._out_dir: str = out_dir
        self._url: str = url or ""

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

        # All Data
        shutil.copy(
            self._datastore.get_file_name(),
            os.path.join(self._out_dir, "database.sqlite"),
        )

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
