import json
import sqlite3
from contextlib import closing

from .jsondeepreaderwriter import JSONDeepReaderWriter
from .models.record import RecordModel
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
                                  json_schema_validation_errors TEXT,
                                  json_schema_validation_pass INT
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
            insert_data = [
                item_id,
                json.dumps(record.data),
                record.git_filename,
            ]
            cur.execute(
                """INSERT INTO record_"""
                + type_id
                + """ (
                id, data, git_filename, json_schema_validation_errors, json_schema_validation_pass 
                ) VALUES (?, ?, ?,  '[]', 0)""",
                insert_data,
            )
            self.connection.commit()

    def store_json_schema_validation_errors(self, type_id, item_id, errors):
        errors_cleaned = []
        for e in errors:
            e["path"] = list(e["path"])
            e["schema_path"] = list(e["schema_path"])
            errors_cleaned.append(e)
        with closing(self.connection.cursor()) as cur:
            update_data = [json.dumps(errors_cleaned), item_id]
            cur.execute(
                """UPDATE record_"""
                + type_id
                + """  SET json_schema_validation_errors=? WHERE ID = ?""",
                update_data,
            )
            self.connection.commit()

    def store_json_schema_validation_pass(self, type_id, item_id):
        with closing(self.connection.cursor()) as cur:
            update_data = [item_id]
            cur.execute(
                """UPDATE record_"""
                + type_id
                + """  SET json_schema_validation_pass=1 WHERE ID = ?""",
                update_data,
            )
            self.connection.commit()

    def get_ids_in_type(self, type_id):
        with closing(self.connection.cursor()) as cur:
            cur.execute("SELECT id FROM record_" + type_id, [])
            return [i["id"] for i in cur.fetchall()]

    def get_item(self, type_id, item_id):
        with closing(self.connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_" + type_id + "  WHERE id=?", [item_id])
            data = cur.fetchone()
            if data:
                record = RecordModel()
                record.load_from_database(data)
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

    def get_file_name(self):
        return self.out_filename
