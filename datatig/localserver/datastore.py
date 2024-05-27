import json
import os
import tempfile

import yaml

import datatig.localserver.settings
from datatig.models.record import RecordModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.readers.directory import process_type
from datatig.repository_access import RepositoryAccessLocalFiles
from datatig.sqlite import DataStoreSQLite
from datatig.validate.jsonschema import JsonSchemaValidator


class DataStore:
    def __init__(self):
        self._database_class = None

    def create(self, source_dir):
        # Create Filename
        temp_dir = tempfile.mkdtemp(prefix="datatig_localserver")
        datatig.localserver.settings.SQLITE_FILE_NAME = os.path.join(
            temp_dir, "database.sqlite"
        )

        # Repository Access
        repository_access = RepositoryAccessLocalFiles(source_dir)

        # Config
        datatig.localserver.settings.SITE_CONFIG = SiteConfigModel(source_dir)
        datatig.localserver.settings.SITE_CONFIG.load_from_file(repository_access)

        # SQLite
        datastore = DataStoreSQLite(
            datatig.localserver.settings.SITE_CONFIG,
            datatig.localserver.settings.SQLITE_FILE_NAME,
            error_if_existing_database=True,
        )

        # Load data
        for type in datatig.localserver.settings.SITE_CONFIG.get_types().values():
            process_type(
                datatig.localserver.settings.SITE_CONFIG,
                repository_access,
                type,
                lambda record: datastore.store(record),
                lambda error: datastore.store_error(error),
            )

        # Validate data
        validate_json_schema = JsonSchemaValidator(
            datatig.localserver.settings.SITE_CONFIG, datastore
        )
        validate_json_schema.go()

    def site_config(self) -> SiteConfigModel:
        return datatig.localserver.settings.SITE_CONFIG  # type: ignore

    def database_class(self):
        if not self._database_class:
            self._database_class = DataStoreSQLite(
                site_config=datatig.localserver.settings.SITE_CONFIG,
                out_filename=datatig.localserver.settings.SQLITE_FILE_NAME,
            )
        return self._database_class

    def update(self, record: RecordModel, data: dict):
        # Save on Disk
        absolute_filename: str = os.path.join(
            self.site_config().get_source_dir(), record.get_git_filename()
        )
        if record.get_format() == "json":
            with open(
                absolute_filename,
                "w",
            ) as fp:
                json.dump(data, fp, indent=record.get_type().get_pretty_json_indent())
        elif record.get_format() == "md":
            data_to_write = data.copy()
            if record.get_type().get_markdown_body_is_field():
                del data_to_write[record.get_type().get_markdown_body_is_field()]
            with open(
                absolute_filename,
                "w",
            ) as fp:
                fp.write("---\n")
                yaml.dump(data_to_write, fp)
                fp.write("---\n\n\n")
                if record.get_type().get_markdown_body_is_field() and data.get(
                    record.get_type().get_markdown_body_is_field()
                ):
                    fp.write(data.get(record.get_type().get_markdown_body_is_field()))  # type: ignore
        elif record.get_format() == "yaml":
            with open(
                absolute_filename,
                "w",
            ) as fp:
                yaml.dump(data, fp)

        # Update in memory
        record._data = data
        for field_id, field_config in record.get_type().get_fields().items():
            record._field_values[field_id] = field_config.get_value_object(
                record=record, data=data
            )

        # Save to database
        self.database_class().store(record)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if self._database_class:
            del self._database_class
