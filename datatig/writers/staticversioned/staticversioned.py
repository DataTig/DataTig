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
        default_ref: str,
        url: Optional[str] = None,
    ):
        self._datastore: DataStoreSQLiteVersioned = datastore
        self._template_variables: dict = {}
        self._out_dir: str = out_dir
        self._url: str = url or ""
        self._default_ref: str = default_ref

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

        # Refs
        for git_commit in self._datastore.get_git_refs():
            self._go_ref(git_commit, jinja2_env)

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
                {"git_commit": git_commit},
                jinja2_env,
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
