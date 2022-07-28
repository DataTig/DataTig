# import datetime
import hashlib
import json
import sqlite3
from contextlib import closing

from datatig.models.siteconfig import SiteConfigModel

# from .exceptions import DuplicateRecordIdException
from .models.error import ErrorModel
from .models.git_commit import GitCommitModel
from .models.record import RecordModel

# from .models.record_error import RecordErrorModel


class DataStoreSQLiteVersioned:
    def __init__(self, out_filename: str):
        self._out_filename: str = out_filename
        self._connection = sqlite3.connect(out_filename)
        self._connection.row_factory = sqlite3.Row

        with closing(self._connection.cursor()) as cur:
            cur.execute(
                """CREATE TABLE config (
                id INTEGER PRIMARY KEY,
                data TEXT,
                hash TEXT UNIQUE
                )"""
            )
            cur.execute(
                """CREATE TABLE git_commit (
                id TEXT PRIMARY KEY,     
                config_id INTEGER           
                )"""
            )
            cur.execute(
                """CREATE TABLE git_ref (
                id TEXT PRIMARY KEY ON CONFLICT REPLACE,
                commit_id TEXT
                )"""
            )
            cur.execute(
                """CREATE TABLE type (
                config_id INTEGER,
                id TEXT ,
                PRIMARY KEY(config_id, id)
                )"""
            )
            cur.execute(
                """CREATE TABLE data (
                id INTEGER PRIMARY KEY,
                data TEXT,
                hash TEXT UNIQUE
                )"""
            )
            cur.execute(
                """CREATE TABLE commit_type_record (
                commit_id TEXT,
                type_id TEXT,
                record_id TEXT,
                data_id INTEGER,
                PRIMARY KEY(commit_id, type_id, record_id)
                )"""
            )
            self._connection.commit()

    def store_config(self, site_config: SiteConfigModel) -> int:
        config_hash: str = site_config.get_hash()
        with closing(self._connection.cursor()) as cur:
            # Look for existing
            cur.execute("SELECT id FROM config WHERE hash=?", [config_hash])
            row = cur.fetchone()
            if row:
                return row["id"]

            # Add new
            cur.execute(
                """INSERT INTO config (hash, data) VALUES (?, ?)""",
                [config_hash, json.dumps(site_config.get_serialised())],
            )
            config_id: int = cur.lastrowid  # type: ignore

            # Add types
            for type in site_config.get_types().values():
                cur.execute(
                    """INSERT INTO type (config_id,  id) VALUES (?, ?)""",
                    [config_id, type.get_id()],
                )
            self._connection.commit()

        return config_id

    def store_git_commit(self, git_commit: GitCommitModel, config_id: int):
        with closing(self._connection.cursor()) as cur:
            # Look for existing
            cur.execute(
                "SELECT id FROM git_commit WHERE id=?", [git_commit.get_commit_hash()]
            )
            row = cur.fetchone()
            if row:
                return

            # Add new
            cur.execute(
                """INSERT INTO git_commit (id, config_id) VALUES (?, ?)""",
                [git_commit.get_commit_hash(), config_id],
            )

            # Refs!
            for ref in git_commit.get_refs():
                cur.execute(
                    """INSERT INTO git_ref (id,  commit_id) VALUES (?, ?)""",
                    [ref, git_commit.get_commit_hash()],
                )

            # Done
            self._connection.commit()

    def store_record(
        self, config_id: int, git_commit: GitCommitModel, record: RecordModel
    ):
        with closing(self._connection.cursor()) as cur:
            data_str = json.dumps(record.get_data(), default=str, sort_keys=True)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()

            # data - existing or new
            cur.execute("SELECT id FROM data WHERE hash=?", [data_hash])
            row = cur.fetchone()
            if row:
                data_id = row["id"]
            else:
                cur.execute(
                    """INSERT INTO data (data, hash) VALUES (?, ?)""",
                    [data_str, data_hash],
                )
                data_id = cur.lastrowid

            # config_commit_type_record  - exisiting or new
            cur.execute(
                "SELECT * FROM commit_type_record WHERE commit_id=? AND type_id=? AND  record_id=?",
                [
                    git_commit.get_commit_hash(),
                    record.get_type().get_id(),
                    record.get_id(),
                ],
            )
            row = cur.fetchone()
            if row:
                pass
            else:
                cur.execute(
                    """INSERT INTO commit_type_record (commit_id, type_id, record_id, data_id) 
                    VALUES (?, ?, ?, ?)""",
                    [
                        git_commit.get_commit_hash(),
                        record.get_type().get_id(),
                        record.get_id(),
                        data_id,
                    ],
                )
            self._connection.commit()

    def store_error(self, error: ErrorModel) -> None:
        print(error.get_message())

    def get_file_name(self) -> str:
        return self._out_filename

    def get_git_refs(self) -> list:
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT * FROM git_ref",
                [],
            )
            return [GitCommitModel(i["commit_id"], [i["id"]]) for i in cur.fetchall()]

    def is_ref_known(self, ref) -> bool:
        with closing(self._connection.cursor()) as cur:
            # ref?
            cur.execute(
                "SELECT * FROM git_ref WHERE id=?",
                [ref],
            )
            row = cur.fetchone()
            if row:
                return True

            # A commit can be a ref too?
            cur.execute(
                "SELECT * FROM git_commit WHERE id=?",
                [ref],
            )
            row = cur.fetchone()
            if row:
                return True

        return False

    def resolve_ref(self, ref) -> str:
        with closing(self._connection.cursor()) as cur:
            # Ref?
            cur.execute(
                "SELECT commit_id FROM git_ref WHERE id=?",
                [ref],
            )
            row = cur.fetchone()
            if row:
                return row["commit_id"]

            # Could have just been passed a commit?
            cur.execute(
                "SELECT id FROM git_commit WHERE id=?",
                [ref],
            )
            row = cur.fetchone()
            if row:
                return row["id"]

        # We failed
        raise Exception("Ref not found!")

    def is_config_same_between_refs(self, ref1: str, ref2: str) -> bool:
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT config_id FROM git_commit WHERE id=?",
                [self.resolve_ref(ref1)],
            )
            config1: int = cur.fetchone()["config_id"]
            cur.execute(
                "SELECT config_id FROM git_commit WHERE id=?",
                [self.resolve_ref(ref2)],
            )
            config2: int = cur.fetchone()["config_id"]
            return config1 == config2
