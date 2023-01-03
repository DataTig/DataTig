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
from .models.record_error import RecordErrorModel

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
                title TEXT,
                description TEXT,
                data TEXT,
                hash TEXT UNIQUE
                )"""
            )
            cur.execute(
                """CREATE TABLE git_commit (
                id TEXT PRIMARY KEY,     
                config_id INTEGER,
                FOREIGN KEY(config_id) REFERENCES config(id)
                )"""
            )
            cur.execute(
                """CREATE TABLE git_ref (
                id TEXT PRIMARY KEY ON CONFLICT REPLACE,
                commit_id TEXT,
                FOREIGN KEY(commit_id) REFERENCES git_commit(id)
                )"""
            )
            cur.execute(
                """CREATE TABLE error (
                commit_id TEXT,
                filename TEXT,
                message TEXT,
                FOREIGN KEY(commit_id) REFERENCES git_commit(id)
                )"""
            )
            cur.execute(
                """CREATE TABLE type (
                config_id INTEGER,
                id TEXT ,
                PRIMARY KEY(config_id, id),
                FOREIGN KEY(config_id) REFERENCES config(id)
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
                git_filename TEXT,
                format TEXT,
                data_id INTEGER,
                PRIMARY KEY(commit_id, type_id, record_id),
                FOREIGN KEY(commit_id) REFERENCES git_commit(id),
                FOREIGN KEY(type_id) REFERENCES type(id),
                FOREIGN KEY(record_id) REFERENCES record(id)
                FOREIGN KEY(data_id) REFERENCES data(id)
                )"""
            )
            cur.execute(
                """CREATE TABLE commit_type_record_error(
                commit_id TEXT,
                type_id TEXT,
                record_id TEXT,
                message TEXT,
                data_path TEXT,
                schema_path TEXT,
                generator TEXT,
                FOREIGN KEY(commit_id) REFERENCES git_commit(id),
                FOREIGN KEY(type_id) REFERENCES type(id),
                FOREIGN KEY(record_id) REFERENCES record(id)
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
                """INSERT INTO config (hash, data, title, description) VALUES (?, ?, ?, ?)""",
                [
                    config_hash,
                    json.dumps(site_config.get_serialised()),
                    site_config.get_title(),
                    site_config.get_description(),
                ],
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

    def store_record(self, git_commit: GitCommitModel, record: RecordModel):
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
                    """INSERT INTO commit_type_record (commit_id, type_id, record_id, data_id, git_filename, format) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    [
                        git_commit.get_commit_hash(),
                        record.get_type().get_id(),
                        record.get_id(),
                        data_id,
                        record.get_git_filename(),
                        record.get_format(),
                    ],
                )
            self._connection.commit()

    def store_error(self, git_commit: GitCommitModel, error: ErrorModel) -> None:
        with closing(self._connection.cursor()) as cur:
            insert_data = [
                git_commit.get_commit_hash(),
                error.get_filename(),
                error.get_message(),
            ]
            cur.execute(
                """INSERT INTO error (
                commit_id, filename, message
                ) VALUES (?, ?, ?)""",
                insert_data,
            )
            self._connection.commit()

    def get_all_errors_generator(self, git_commit: GitCommitModel):
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT * FROM error WHERE commit_id=?", [git_commit.get_commit_hash()]
            )
            for data in cur.fetchall():
                m = ErrorModel()
                m.load_from_database(data)
                yield m

    def get_count_site_errors(self, git_commit: GitCommitModel) -> int:
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT count(*) AS c FROM error WHERE commit_id=?",
                [git_commit.get_commit_hash()],
            )
            return cur.fetchone()["c"]

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

    def get_data_differences_between_refs(self, ref1: str, ref2: str) -> list:
        commit1 = self.resolve_ref(ref1)
        commit2 = self.resolve_ref(ref2)
        out = []
        with closing(self._connection.cursor()) as cur:

            # compare data items that exist in both
            cur.execute(
                "SELECT  c1.type_id, c1.record_id FROM commit_type_record AS c1 "
                + "JOIN commit_type_record AS c2 ON c1.type_id = c2.type_id AND c1.record_id = c2.record_id "
                + "WHERE c1.commit_id=? AND c2.commit_id = ? "
                + "AND c1.data_id != c2.data_id",
                [commit1, commit2],
            )
            for row in cur.fetchall():
                out.append(
                    {
                        "type_id": row["type_id"],
                        "record_id": row["record_id"],
                        "action": "edited",
                    }
                )

            # Items that have been removed or added
            for params, action in [
                ([commit2, commit1], "removed"),
                ([commit1, commit2], "added"),
            ]:
                cur.execute(
                    "SELECT  c1.type_id, c1.record_id FROM commit_type_record AS c1 "
                    + "LEFT JOIN commit_type_record AS c2 ON c1.type_id = c2.type_id AND c1.record_id = c2.record_id AND c2.commit_id = ? "
                    + "WHERE c1.commit_id=?  "
                    + "AND c2.data_id IS NULL",
                    params,
                )
                for row in cur.fetchall():
                    out.append(
                        {
                            "type_id": row["type_id"],
                            "record_id": row["record_id"],
                            "action": action,
                        }
                    )
        # return
        return out

    def get_errors_added_between_refs(self, ref1: str, ref2: str) -> list:
        commit1 = self.resolve_ref(ref1)
        commit2 = self.resolve_ref(ref2)
        out = []
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT e2.* "
                + "FROM error AS e2 "
                + "LEFT JOIN error AS e1 ON e1.filename = e2.filename AND e1.message = e2.message AND e1.commit_id=? "
                + "WHERE e2.commit_id = ? AND e1.filename IS NULL",
                [commit1, commit2],
            )
            for row in cur.fetchall():
                m = ErrorModel()
                m.load_from_database(row)
                out.append(m)
        return out

    def get_errors_removed_between_refs(self, ref1: str, ref2: str) -> list:
        return self.get_errors_added_between_refs(ref2, ref1)

    def get_config(self, ref_or_commit: str):
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT config_id FROM git_commit WHERE id=?",
                [self.resolve_ref(ref_or_commit)],
            )
            config_id: int = cur.fetchone()["config_id"]
            cur.execute(
                "SELECT data FROM config WHERE id=?",
                [config_id],
            )
            config_row = cur.fetchone()
            config: SiteConfigModel = SiteConfigModel("/source_dir_does_not_exist")
            config.load_from_serialised(json.loads(config_row["data"]))
            return config

    def get_ids_in_type(self, ref_or_commit: str, type_id: str):
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT record_id FROM commit_type_record WHERE type_id=? AND commit_id=?",
                [type_id, self.resolve_ref(ref_or_commit)],
            )
            return [i["record_id"] for i in cur.fetchall()]

    def get_item(self, ref_or_commit: str, type_id: str, record_id: str):
        commit_hash = self.resolve_ref(ref_or_commit)
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT * FROM commit_type_record WHERE commit_id=? AND type_id=? AND record_id=?",
                [commit_hash, type_id, record_id],
            )
            commit_type_record_row = cur.fetchone()
            if commit_type_record_row:
                # Data
                cur.execute(
                    "SELECT data FROM data  WHERE id=?",
                    [commit_type_record_row["data_id"]],
                )
                data_row = cur.fetchone()
                # Errors
                cur.execute(
                    "SELECT * FROM commit_type_record_error  WHERE commit_id=? AND type_id=? AND record_id=?",
                    [commit_hash, type_id, record_id],
                )
                errors_data = cur.fetchall()
                # Create model and return
                record = RecordModel(
                    # TODO self.get_config().get_type() is very ineffeicent, would be better if type class instance was passed instead of type_id
                    type=self.get_config(self.resolve_ref(ref_or_commit)).get_type(
                        type_id
                    ),
                    id=record_id,
                )
                record.load_from_versioned_database(
                    commit_type_record_row, data_row, errors_data=errors_data
                )
                return record

    def store_json_schema_validation_errors(
        self, ref_or_commit: str, type_id: str, item_id: str, errors
    ) -> None:
        with closing(self._connection.cursor()) as cur:
            for error in errors:
                insert_data = [
                    ref_or_commit,
                    type_id,
                    item_id,
                    error["message"],
                    error["path_str"],
                    error["schema_path_str"],
                    "jsonschema",
                ]
                cur.execute(
                    """INSERT INTO commit_type_record_error (
                    commit_id, type_id, record_id, message, data_path, schema_path, generator
                    ) VALUES (?, ?, ?,  ?, ?, ?, ?)""",
                    insert_data,
                )
            self._connection.commit()

    def get_record_errors_added_between_refs_for_record(
        self, ref1: str, ref2: str, type_id: str, record_id: str
    ) -> list:
        commit1 = self.resolve_ref(ref1)
        commit2 = self.resolve_ref(ref2)
        out = []
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT e2.* "
                + "FROM commit_type_record_error AS e2 "
                + "LEFT JOIN commit_type_record_error AS e1 ON "
                + "e1.message = e2.message AND e1.data_path = e2.data_path "
                + "AND e1.schema_path = e2.schema_path AND e1.generator = e2.generator "
                + "AND e1.commit_id=? AND e1.type_id=? AND e1.record_id=? "
                + "WHERE e2.commit_id = ? AND e2.type_id=? AND e2.record_id=? AND e1.commit_id IS NULL",
                [commit1, type_id, record_id, commit2, type_id, record_id],
            )
            for row in cur.fetchall():
                m = RecordErrorModel()
                m.load_from_database(row)
                out.append(m)
        return out

    def get_record_errors_removed_between_refs_for_record(
        self, ref1: str, ref2: str, type_id: str, record_id: str
    ) -> list:
        return self.get_record_errors_added_between_refs_for_record(
            ref2, ref1, type_id, record_id
        )
