import json
import sqlite3
from contextlib import closing

from datatig.models.siteconfig import SiteConfigModel

from .exceptions import DuplicateRecordIdException
from .models.calendar_event import CalendarEventModel
from .models.error import ErrorModel
from .models.record import RecordModel
from .models.record_error import RecordErrorModel
from .models.type import TypeModel


class DataStoreSQLite:
    def __init__(
        self,
        site_config: SiteConfigModel,
        out_filename: str,
        error_if_existing_database: bool = False,
    ):
        self._site_config: SiteConfigModel = site_config
        self._out_filename: str = out_filename
        self._connection = sqlite3.connect(out_filename)
        self._connection.row_factory = sqlite3.Row
        self._was_existing_database: bool = self._is_existing_database()
        if self._was_existing_database and error_if_existing_database:
            raise Exception("The SQLITE database file already exists.")
        if not self._was_existing_database:
            self._create()

    def _is_existing_database(self) -> bool:
        with closing(self._connection.cursor()) as cur:
            # Check
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='type'",
                [],
            )
            return bool(cur.fetchone())

    def _create(self):
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                """CREATE TABLE site_config (
                key TEXT,
                value TEXT
                )"""
            )
            cur.execute(
                """CREATE TABLE error (
                filename TEXT,
                message TEXT
                )"""
            )
            cur.execute(
                """CREATE TABLE type (
                id TEXT PRIMARY KEY,
                directory TEXT,
                json_schema TEXT,
                list_fields TEXT,
                pretty_json_indent INTEGER,
                default_format TEXT,
                markdown_body_is_field TEXT
                )"""
            )
            cur.execute(
                """CREATE TABLE type_field (
                type_id TEXT ,
                id TEXT,
                key TEXT,
                type TEXT,
                title TEXT,
                description TEXT,
                sort INTEGER NOT NULL,
                extra_config TEXT,
                PRIMARY KEY(type_id, id),
                FOREIGN KEY(type_id) REFERENCES type(id)
                )"""
            )

            self._create_site_config(cur)

            for type in self._site_config.get_types().values():
                self._create_type(cur, type)

            self._create_calendars(cur)

    def _create_site_config(self, cur):
        for k, v in {
            "title": self._site_config.get_title(),
            "description": self._site_config.get_description(),
            "githost/url": self._site_config.get_github_url(),
            "githost/primary_branch": self._site_config.get_githost_primary_branch(),
        }.items():
            cur.execute(
                """INSERT INTO site_config (key, value) VALUES (?, ?)""",
                [k, v],
            )

    def _create_type(self, cur, type: TypeModel):

        cur.execute(
            """INSERT INTO type (
            id, directory, json_schema, list_fields, pretty_json_indent, default_format, markdown_body_is_field
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                type.get_id(),
                type.get_directory(),
                json.dumps(type.get_json_schema_as_dict()),
                json.dumps(type.get_list_fields()),
                type.get_pretty_json_indent(),
                type.get_default_format(),
                type.get_markdown_body_is_field(),
            ],
        )

        cur.execute(
            """CREATE TABLE record_{type} (
                          id TEXT PRIMARY KEY,
                          data TEXT,
                          git_filename TEXT,
                          format TEXT
                      )""".format(
                type=type.get_id()
            ),
            [],
        )

        cur.execute(
            """CREATE TABLE record_error_{type} (
                          record_id TEXT,
                          message TEXT,
                          data_path TEXT,
                          schema_path TEXT,
                          generator TEXT,
                          FOREIGN KEY(record_id) REFERENCES record_{type}(id)
                      )""".format(
                type=type.get_id()
            ),
            [],
        )

        self._type_field_sort: int = 1
        for type_field_id, type_field in type.get_fields().items():
            self._create_type_add_field(cur, type, type_field)

    def _create_type_add_field(self, cur, type, type_field, parent_keys=[]):
        cur.execute(
            """INSERT INTO type_field (
            type_id , id, key, type, title, description, sort, extra_config
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                type.get_id(),
                "/".join(parent_keys + [type_field.get_id()]),
                type_field.get_key(),
                type_field.get_type(),
                type_field.get_title(),
                type_field.get_description(),
                self._type_field_sort,
                json.dumps(type_field.get_extra_config()),
            ],
        )
        self._type_field_sort += 1

        table_name = "record_" + type.get_id()
        for parent_key in parent_keys:
            table_name += "___field_" + parent_key

        if type_field.get_type() in [
            "url",
            "string",
            "list-strings",
            "markdown",
        ]:
            cur.execute(
                """ALTER TABLE """
                + table_name
                + """ ADD field_"""
                + type_field.get_id()
                + """ TEXT """,
                [],
            )
        elif type_field.get_type() in [
            "datetime",
            "date",
        ]:
            cur.execute(
                """ALTER TABLE """
                + table_name
                + """ ADD field_"""
                + type_field.get_id()
                + """ TEXT """,
                [],
            )
            cur.execute(
                """ALTER TABLE """
                + table_name
                + """ ADD field_"""
                + type_field.get_id()
                + """___timestamp INTEGER """,
                [],
            )
        elif type_field.get_type() in ["boolean", "integer"]:
            cur.execute(
                """ALTER TABLE """
                + table_name
                + """ ADD field_"""
                + type_field.get_id()
                + """ INTEGER """,
                [],
            )
        if type_field.get_type() in ["list-strings"]:
            cur.execute(
                """CREATE TABLE {table}___field_{field} (
                    record_id TEXT, 
                    sort INTEGER NOT NULL,
                    value TEXT,
                    FOREIGN KEY(record_id) REFERENCES record_{type}(id)
                    ) 
                    """.format(
                    table=table_name, type=type.get_id(), field=type_field.get_id()
                ),
                [],
            )
        elif type_field.get_type() in ["list-dictionaries"]:
            cur.execute(
                """CREATE TABLE {table}___field_{field} (
                    record_id TEXT NOT NULL, 
                    sort INTEGER NOT NULL,
                    FOREIGN KEY(record_id) REFERENCES record_{type}(id)
                    ) 
                    """.format(
                    table=table_name, type=type.get_id(), field=type_field.get_id()
                ),
                [],
            )
            for sub_type_field in type_field.get_fields().values():
                self._create_type_add_field(
                    cur,
                    type,
                    sub_type_field,
                    parent_keys=parent_keys + [type_field.get_id()],
                )

    def _create_calendars(self, cur):
        # Calendars!
        # Always create basic table, so consuming apps can easily SELECT and see if there are any calendars or not.
        cur.execute(
            """CREATE TABLE calendar (
                id TEXT,
                timezone TEXT
                )"""
        )
        # Only create more tables if there is actually data,
        # to avoid filling DB's with unused confusing tables for simple sites that don't use extra features.
        if self._site_config.get_calendars() and self._site_config.get_types().values():
            cur.execute(
                """CREATE TABLE calendar_event (
                    calendar_id TEXT,
                    id TEXT,
                    summary TEXT,
                    start_iso TEXT,
                    start_timestamp INTEGER,
                    end_iso TEXT,
                    end_timestamp INTEGER, """
                + ", ".join(
                    [
                        "record_" + type.get_id() + "___id TEXT "
                        for type in self._site_config.get_types().values()
                    ]
                )
                + """, """
                + ", ".join(
                    [
                        "FOREIGN KEY (record_"
                        + type.get_id()
                        + """___id) REFERENCES record_"""
                        + type.get_id()
                        + "(id)"
                        for type in self._site_config.get_types().values()
                    ]
                )
                + """
                    , FOREIGN KEY(calendar_id) REFERENCES calendar(id)
                    )"""
            )

        self._connection.commit()

    def store(self, record: RecordModel) -> None:
        with closing(self._connection.cursor()) as cur:
            # Delete old data first?
            if self._was_existing_database:
                cur.execute(
                    "DELETE FROM record_" + record.get_type().get_id() + "  WHERE id=?",
                    [record.get_id()],
                )

                for field in record.get_type().get_fields().values():
                    if field.get_type() in ["list-strings", "list-dictionaries"]:
                        cur.execute(
                            """DELETE FROM record_"""
                            + record.get_type().get_id()
                            + """___field_"""
                            + field.get_id()
                            + """ WHERE record_id=? """,
                            [record.get_id()],
                        )

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
            insert_fields, insert_data = self._store_get_fields_and_values(
                record.get_type().get_fields().values(),
                lambda field_id: record.get_field_value(field_id),
            )
            insert_fields += ["id", "data", "git_filename", "format"]
            insert_data += [
                record.get_id(),
                json.dumps(record.get_data(), default=str),
                record.get_git_filename(),
                record.get_format(),
            ]
            cur.execute(
                """INSERT INTO record_"""
                + record.get_type().get_id()
                + """ (
                """
                + ", ".join(insert_fields)
                + """
                ) VALUES ("""
                + ", ".join(["?" for i in insert_fields])
                + """)""",
                insert_data,
            )

            for field in record.get_type().get_fields().values():
                value_object = record.get_field_value(field.get_id())
                value = value_object.get_value()
                if (
                    field.get_type() in ["list-strings"]
                    and isinstance(value, list)
                    and len(value) > 0
                ):
                    sort = 1
                    for v in value:
                        cur.execute(
                            """INSERT INTO  record_"""
                            + record.get_type().get_id()
                            + """___field_"""
                            + field.get_id()
                            + """ (record_id, sort, value) VALUES (?, ?, ?) """,
                            [record.get_id(), sort, str(v)],
                        )
                        sort += 1
                elif field.get_type() in ["list-dictionaries"]:
                    sort = 1
                    for sub_record in value_object.get_sub_records():
                        insert_fields, insert_data = self._store_get_fields_and_values(
                            field.get_fields().values(),
                            lambda field_id: sub_record.get_value(field_id),
                        )
                        insert_fields += ["record_id", "sort"]
                        insert_data += [
                            record.get_id(),
                            sort,
                        ]
                        sort += 1
                        cur.execute(
                            """INSERT INTO record_"""
                            + record.get_type().get_id()
                            + """___field_"""
                            + field.get_id()
                            + """ (
                                       """
                            + ", ".join(insert_fields)
                            + """
                                       ) VALUES ("""
                            + ", ".join(["?" for i in insert_fields])
                            + """)""",
                            insert_data,
                        )

            self._connection.commit()

    def _store_get_fields_and_values(self, fields, value_object_getter_function):
        out_fields = []
        out_values = []
        for field in fields:
            value_object = value_object_getter_function(field.get_id())
            value = value_object.get_value()
            if field.get_type() in [
                "url",
                "string",
                "markdown",
            ] and isinstance(value, str):
                out_fields.append("field_" + field.get_id())
                out_values.append(value)
            elif field.get_type() in [
                "datetime",
                "date",
            ] and isinstance(value, str):

                out_fields.append("field_" + field.get_id())
                out_values.append(value)
                out_fields.append("field_" + field.get_id() + "___timestamp")
                out_values.append(value_object.get_value_timestamp())
            elif (
                field.get_type() in ["list-strings"]
                and isinstance(value, list)
                and len(value) > 0
            ):

                out_fields.append("field_" + field.get_id())
                out_values.append(", ".join([str(v) for v in value]))
            elif field.get_type() == "boolean" and isinstance(value, bool):

                out_fields.append("field_" + field.get_id())
                out_values.append(1 if value else 0)
            elif field.get_type() == "integer" and isinstance(value, int):
                out_fields.append("field_" + field.get_id())
                out_values.append(value)

        return out_fields, out_values

    def store_json_schema_validation_errors(self, type_id, item_id, errors) -> None:
        with closing(self._connection.cursor()) as cur:
            for error in errors:
                insert_data = [
                    item_id,
                    error["message"],
                    error["path_str"],
                    error["schema_path_str"],
                    "jsonschema",
                ]
                cur.execute(
                    """INSERT INTO record_error_"""
                    + type_id
                    + """ (
                    record_id, message, data_path, schema_path, generator
                    ) VALUES (?, ?, ?,  ?, ?)""",
                    insert_data,
                )
            self._connection.commit()

    def get_all_record_errors_generator_in_type(self, type_id):
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_error_" + type_id, [])
            for data in cur.fetchall():
                m = RecordErrorModel()
                m.load_from_database(data)
                yield m

    def get_ids_in_type(self, type_id: str) -> list:
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT id FROM record_" + type_id, [])
            return [i["id"] for i in cur.fetchall()]

    def get_ids_in_type_with_record_error(self, type_id) -> list:
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "SELECT r.id FROM record_"
                + type_id
                + " AS r  JOIN record_error_"
                + type_id
                + " AS re ON r.id = re.record_id GROUP BY r.id ",
                [],
            )
            return [i["id"] for i in cur.fetchall()]

    def get_item(self, type_id: str, item_id: str):
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_" + type_id + "  WHERE id=?", [item_id])
            data = cur.fetchone()
            if data:
                cur.execute(
                    "SELECT * FROM record_error_" + type_id + "  WHERE record_id=?",
                    [item_id],
                )
                errors_data = cur.fetchall()
                record = RecordModel(
                    type=self._site_config.get_type(type_id), id=item_id
                )
                record.load_from_database(
                    data,
                    errors_data=errors_data,
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

    def get_count_site_errors(self) -> int:
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT count(*) AS c FROM error", [])
            return cur.fetchone()["c"]

    def get_count_record_errors_for_type(self, type_id) -> int:
        # must check type_id passed is valid, or this could be an SQL injection issue
        if not type_id in self._site_config.get_types().keys():
            raise Exception("That type_id is not known!")
        with closing(self._connection.cursor()) as cur:
            cur.execute("SELECT count(*) AS c FROM record_error_" + type_id, [])
            return cur.fetchone()["c"]

    def get_count_record_errors(self) -> int:
        count = 0
        for type in self._site_config.get_types().values():
            count += self.get_count_record_errors_for_type(type.get_id())
        return count

    def get_file_name(self) -> str:
        return self._out_filename

    def process_calendars(self) -> None:
        for calendar_id, calendar_config in self._site_config.get_calendars().items():
            with closing(self._connection.cursor()) as cur:
                cur.execute(
                    "INSERT INTO calendar (id, timezone) VALUES (?, ?)",
                    [calendar_id, calendar_config.get_timezone()],
                )
                for data_config in calendar_config.get_datas():
                    for item_id in self.get_ids_in_type(data_config.get_type_id()):
                        item = self.get_item(data_config.get_type_id(), item_id)
                        calendar_event = CalendarEventModel()
                        if calendar_event.load_from_calendar_data_and_item(
                            data_config, item
                        ):
                            cur.execute(
                                "INSERT INTO calendar_event (calendar_id, id, summary, start_iso, start_timestamp, end_iso, end_timestamp, record_"
                                + data_config.get_type_id()
                                + "___id ) "
                                + "VALUES (?,?,?,?,?,?,?,?)",
                                [
                                    calendar_id,
                                    calendar_event.get_id(),
                                    calendar_event.get_summary(),
                                    calendar_event.get_start_iso(),
                                    calendar_event.get_start_timestamp(),
                                    calendar_event.get_end_iso(),
                                    calendar_event.get_end_timestamp(),
                                    item.get_id(),
                                ],
                            )

                self._connection.commit()

    def get_calendar_events_in_calendar(self, calendar_id: str) -> list:
        if not self._site_config.get_calendars():
            return []
        with closing(self._connection.cursor()) as cur:
            out = []
            cur.execute(
                "SELECT * FROM calendar_event WHERE calendar_id=? ORDER BY start_timestamp ASC",
                [calendar_id],
            )
            for data in cur.fetchall():
                ce = CalendarEventModel()
                ce.load_from_database(data)
                out.append(ce)
            return out

    def get_calendar_events_in_record(self, record: RecordModel) -> list:
        if not self._site_config.get_calendars():
            return []
        with closing(self._connection.cursor()) as cur:
            out = []
            cur.execute(
                "SELECT * FROM calendar_event WHERE record_"
                + record.get_type().get_id()
                + "___id=? ORDER BY start_timestamp ASC",
                [record.get_id()],
            )
            for data in cur.fetchall():
                ce = CalendarEventModel()
                ce.load_from_database(data)
                out.append(ce)
            return out
