import json
import sqlite3
from contextlib import closing

from .exceptions import DuplicateRecordIdException
from .jsondeepreaderwriter import JSONDeepReaderWriter
from .models.error import ErrorModel
from .models.record import RecordModel
from .models.record_json_schema_validation_error import (
    RecordJSONSchemaValidationErrorModel,
)
from .models.type_field import TypeFieldModel


class DataStoreSQLite:
    def __init__(self, site_config, out_filename):
        self.site_config = site_config
        self.out_filename = out_filename
        self.connection = sqlite3.connect(out_filename)
        self.connection.row_factory = sqlite3.Row

        # Create table
        with closing(self.connection.cursor()) as cur:
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

            for type in site_config.types.values():
                cur.execute(
                    """INSERT INTO type (
                    id 
                    ) VALUES (?)""",
                    [type.id],
                )

                cur.execute(
                    """CREATE TABLE record_"""
                    + type.id
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
                    + type.id
                    + """  (
                                  record_id TEXT,
                                  message TEXT,
                                  data_path TEXT,
                                  schema_path TEXT
                              )""",
                    [],
                )

                for type_field_id, type_field in type.fields.items():
                    cur.execute(
                        """INSERT INTO type_field (
                        type_id , id, key, type, title
                        ) VALUES (?, ?, ?, ?, ?)""",
                        [
                            type.id,
                            type_field_id,
                            type_field.key(),
                            type_field.type(),
                            type_field.title(),
                        ],
                    )

            self.connection.commit()

    def store(self, type_id, item_id, record):
        with closing(self.connection.cursor()) as cur:
            # Check
            cur.execute("SELECT * FROM record_" + type_id + "  WHERE id=?", [item_id])
            data = cur.fetchone()
            if data:
                raise DuplicateRecordIdException(
                    "The id "
                    + item_id
                    + " is duplicated in "
                    + record.git_filename
                    + " and "
                    + data["git_filename"]
                )

            # Store
            insert_data = [
                item_id,
                json.dumps(record.data),
                record.git_filename,
                record.format,
            ]
            cur.execute(
                """INSERT INTO record_"""
                + type_id
                + """ (
                id, data, git_filename, format
                ) VALUES (?, ?, ?,  ?)""",
                insert_data,
            )
            self.connection.commit()

    def store_json_schema_validation_errors(self, type_id, item_id, errors):
        with closing(self.connection.cursor()) as cur:
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
            self.connection.commit()

    def get_all_json_schema_validation_errors_generator(self, type_id):
        with closing(self.connection.cursor()) as cur:
            cur.execute(
                "SELECT * FROM record_json_schema_validation_error_" + type_id, []
            )
            for data in cur.fetchall():
                m = RecordJSONSchemaValidationErrorModel()
                m.load_from_database(data)
                yield m

    def get_ids_in_type(self, type_id):
        with closing(self.connection.cursor()) as cur:
            cur.execute("SELECT id FROM record_" + type_id, [])
            return [i["id"] for i in cur.fetchall()]

    def get_item(self, type_id, item_id):
        with closing(self.connection.cursor()) as cur:
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
                record = RecordModel()
                record.load_from_database(
                    data,
                    json_schema_validation_errors_data=json_schema_validation_errors_data,
                )
                return record

    def get_field(self, type_id, item_id, field_id):
        with closing(self.connection.cursor()) as cur:
            # Load Field Type
            cur.execute(
                "SELECT * FROM type_field  WHERE type_id=? AND id=?",
                [type_id, field_id],
            )
            data = cur.fetchone()
            if data:
                type_field = TypeFieldModel()
                type_field.load_from_database(data)
                # Load Record
                cur.execute(
                    "SELECT * FROM record_" + type_id + "  WHERE id=?", [item_id]
                )
                data = cur.fetchone()
                if data:
                    record = RecordModel()
                    record.load_from_database(data)
                    # Now get value
                    obj = JSONDeepReaderWriter(record.data)
                    return obj.read(type_field.key())

    def store_error(self, error):
        with closing(self.connection.cursor()) as cur:
            insert_data = [
                error.filename,
                error.message,
            ]
            cur.execute(
                """INSERT INTO error (
                filename, message
                ) VALUES (?, ?)""",
                insert_data,
            )
            self.connection.commit()

    def get_all_errors_generator(self):
        with closing(self.connection.cursor()) as cur:
            cur.execute("SELECT * FROM error", [])
            for data in cur.fetchall():
                m = ErrorModel()
                m.load_from_database(data)
                yield m

    def get_count_errors(self):
        with closing(self.connection.cursor()) as cur:
            cur.execute("SELECT count(*) AS c FROM error", [])
            return cur.fetchone()["c"]

    def get_file_name(self):
        return self.out_filename
