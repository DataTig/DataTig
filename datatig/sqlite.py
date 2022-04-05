import datetime
import json
import sqlite3
from contextlib import closing

from datatig.models.siteconfig import SiteConfigModel

from .exceptions import DuplicateRecordIdException
from .jsondeepreaderwriter import JSONDeepReaderWriter
from .models.error import ErrorModel
from .models.record import RecordModel
from .models.record_json_schema_validation_error import (
    RecordJSONSchemaValidationErrorModel,
)


class DataStoreSQLite:
    def __init__(self, site_config: SiteConfigModel, out_filename: str):
        self._site_config: SiteConfigModel = site_config
        self._out_filename: str = out_filename
        self._connection = sqlite3.connect(out_filename)
        self._connection.row_factory = sqlite3.Row

        # Create table
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                """CREATE TABLE error (
                filename TEXT,
                message TEXT
                )"""
            )
            cur.execute(
                """CREATE TABLE type (
                id TEXT PRIMARY KEY,
                fields TEXT
                )"""
            )
            cur.execute(
                """CREATE TABLE type_field (
                type_id TEXT ,
                id TEXT,
                key TEXT,
                type TEXT,
                title TEXT,
                PRIMARY KEY(type_id, id)
                )"""
            )

            for type in site_config.get_types().values():
                cur.execute(
                    """INSERT INTO type (
                    id 
                    ) VALUES (?)""",
                    [type.get_id()],
                )

                cur.execute(
                    """CREATE TABLE record_"""
                    + type.get_id()
                    + """  (
                                  id TEXT PRIMARY KEY,
                                  data TEXT,
                                  git_filename TEXT,
                                  format TEXT
                              )""",
                    [],
                )

                cur.execute(
                    """CREATE TABLE record_json_schema_validation_error_"""
                    + type.get_id()
                    + """  (
                                  record_id TEXT,
                                  message TEXT,
                                  data_path TEXT,
                                  schema_path TEXT
                              )""",
                    [],
                )

                for type_field_id, type_field in type.get_fields().items():
                    cur.execute(
                        """INSERT INTO type_field (
                        type_id , id, key, type, title
                        ) VALUES (?, ?, ?, ?, ?)""",
                        [
                            type.get_id(),
                            type_field_id,
                            type_field.get_key(),
                            type_field.get_type(),
                            type_field.get_title(),
                        ],
                    )

                    if type_field.get_type() in [
                        "url",
                        "string",
                        "list-strings",
                        "date",
                        "datetime",
                    ]:
                        cur.execute(
                            """ALTER TABLE record_"""
                            + type.get_id()
                            + """ ADD field_"""
                            + type_field_id
                            + """ TEXT """,
                            [],
                        )
                    if type_field.get_type() in ["list-strings"]:
                        cur.execute(
                            """CREATE TABLE record_"""
                            + type.get_id()
                            + """_field_"""
                            + type_field_id
                            + """ (record_id TEXT, value TEXT) """,
                            [],
                        )

            self._connection.commit()

    def store(self, record: RecordModel) -> None:
        with closing(self._connection.cursor()) as cur:
            # Check
            cur.execute(
                "SELECT * FROM record_" + record.get_type().get_id() + "  WHERE id=?",
                [record.get_id()],
            )
            data = cur.fetchone()
            if data:
                raise DuplicateRecordIdException(
                    "The id "
                    + record.get_id()
                    + " is duplicated in "
                    + record.get_git_filename()
                    + " and "
                    + data["git_filename"]
                )

            # Store
            insert_data = [
                record.get_id(),
                json.dumps(record.get_data(), default=str),
                record.get_git_filename(),
                record.get_format(),
            ]
            cur.execute(
                """INSERT INTO record_"""
                + record.get_type().get_id()
                + """ (
                id, data, git_filename, format
                ) VALUES (?, ?, ?,  ?)""",
                insert_data,
            )

            for field in record.get_type().get_fields().values():
                value = JSONDeepReaderWriter(record.get_data()).read(field.get_key())
                if field.get_type() in [
                    "url",
                    "string",
                    "date",
                    "datetime",
                ] and isinstance(value, str):
                    cur.execute(
                        """UPDATE record_"""
                        + record.get_type().get_id()
                        + """ SET field_"""
                        + field.get_id()
                        + """ = ? WHERE id=?""",
                        [value, record.get_id()],
                    )
                if field.get_type() == "date" and isinstance(value, datetime.date):
                    cur.execute(
                        """UPDATE record_"""
                        + record.get_type().get_id()
                        + """ SET field_"""
                        + field.get_id()
                        + """ = ? WHERE id=?""",
                        [value.isoformat(), record.get_id()],
                    )
                if field.get_type() == "datetime" and isinstance(
                    value, datetime.datetime
                ):
                    cur.execute(
                        """UPDATE record_"""
                        + record.get_type().get_id()
                        + """ SET field_"""
                        + field.get_id()
                        + """ = ? WHERE id=?""",
                        [value.isoformat(), record.get_id()],
                    )
                if field.get_type() in ["list-strings"] and isinstance(value, list):
                    cur.execute(
                        """UPDATE record_"""
                        + record.get_type().get_id()
                        + """ SET field_"""
                        + field.get_id()
                        + """ = ? WHERE id=?""",
                        [", ".join([str(v) for v in value]), record.get_id()],
                    )
                    for v in value:
                        cur.execute(
                            """INSERT INTO  record_"""
                            + record.get_type().get_id()
                            + """_field_"""
                            + field.get_id()
                            + """ (record_id, value) VALUES (?, ?) """,
                            [record.get_id(), str(v)],
                        )

            self._connection.commit()

    def store_json_schema_validation_errors(self, type_id, item_id, errors) -> None:
        with closing(self._connection.cursor()) as cur:
            for error in errors:
                insert_data = [
                    item_id,
                    error["message"],
                    error["path_str"],
                    error["schema_path_str"],
                ]
                cur.execute(
                    """INSERT INTO record_json_schema_validation_error_"""
                    + type_id
                    + """ (
                    record_id, message, data_path, schema_path 
                    ) VALUES (?, ?, ?,  ?)""",
                    insert_data,
                )
            self._connection.commit()

    def get_all_json_schema_validation_errors_generator(self, type_id):
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT * FROM record_json_schema_validation_error_" + type_id, []
            )
            for data in cur.fetchall():
                m = RecordJSONSchemaValidationErrorModel()
                m.load_from_database(data)
                yield m

    def get_ids_in_type(self, type_id) -> list:
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT id FROM record_" + type_id, [])
            return [i["id"] for i in cur.fetchall()]

    def get_item(self, type_id, item_id):
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_" + type_id + "  WHERE id=?", [item_id])
            data = cur.fetchone()
            if data:
                cur.execute(
                    "SELECT * FROM record_json_schema_validation_error_"
                    + type_id
                    + "  WHERE record_id=?",
                    [item_id],
                )
                json_schema_validation_errors_data = cur.fetchall()
                record = RecordModel(
                    type=self._site_config.get_type(type_id), id=item_id
                )
                record.load_from_database(
                    data,
                    json_schema_validation_errors_data=json_schema_validation_errors_data,
                )
                return record

    def store_error(self, error) -> None:
        with closing(self._connection.cursor()) as cur:
            insert_data = [
                error.get_filename(),
                error.get_message(),
            ]
            cur.execute(
                """INSERT INTO error (
                filename, message
                ) VALUES (?, ?)""",
                insert_data,
            )
            self._connection.commit()

    def get_all_errors_generator(self):
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT * FROM error", [])
            for data in cur.fetchall():
                m = ErrorModel()
                m.load_from_database(data)
                yield m

    def get_count_errors(self) -> int:
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT count(*) AS c FROM error", [])
            return cur.fetchone()["c"]

    def get_file_name(self) -> str:
        return self._out_filename
