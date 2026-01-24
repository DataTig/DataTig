import os.path
import tempfile

from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe

import datatig.repository_access
from datatig.models.siteconfig import SiteConfigModel
from datatig.readers.directory import process_type
from datatig.sqlite import DataStoreSQLite
from datatig.staticpipes.collection import DataTigCollection
from datatig.validate.jsonschema import JsonSchemaValidator


class PipeDataTigLoad(BasePipe):

    def __init__(self, directory=""):
        self.directory = directory

    def get_pass_numbers(self) -> list:
        return [100]

    def start_build(self, current_info: CurrentInfo) -> None:

        absolute_directory = (
            os.path.join(self.source_directory.dir, self.directory)
            if self.directory and self.directory != "/"
            else self.source_directory.dir
        )

        # Repository Access
        repository_access = datatig.repository_access.RepositoryAccessLocalFiles(
            absolute_directory
        )

        # Config
        config = SiteConfigModel(absolute_directory)
        config.load_from_file(repository_access)

        # SQLite
        temp_dir = tempfile.mkdtemp()
        sqlite_filename = os.path.join(temp_dir, "datatig.sqlite")
        datastore = DataStoreSQLite(
            config, sqlite_filename, error_if_existing_database=True
        )

        # Load data
        for type in config.get_types().values():
            process_type(
                config,
                repository_access,
                type,
                lambda record: datastore.store(record),
                lambda error: datastore.store_error(error),
            )

        # Validate data
        validate_json_schema = JsonSchemaValidator(config, datastore)
        validate_json_schema.go()

        # Calendars
        datastore.process_calendars()

        # Into context
        current_info.set_context(
            "datatig",
            {
                "sqlite_file_size_bytes": os.path.getsize(sqlite_filename),
                "config": config,
                "datastore": datastore,
                "sqlite_filename": sqlite_filename,
            },
        )
        for type_id, type_config in config.get_types().items():
            current_info.set_context(
                ["collection", type_id], DataTigCollection(config, datastore, type_id)
            )
