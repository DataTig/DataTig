import os
import shutil
import sys
import tempfile

from .readers.directory import process_type
from .siteconfig import SiteConfig
from .sqlite import DataStoreSQLite
from .validate.jsonschema import JsonSchemaValidator
from .writers.static import StaticWriter


def go(source_dir, staticsite_output=None, sqlite_output=None):

    temp_dir = None
    if sqlite_output is None:
        temp_dir = tempfile.mkdtemp()
        sqlite_output = os.path.join(temp_dir, "database.sqlite")

    config = SiteConfig(source_dir)
    config.load_from_file()

    datastore = DataStoreSQLite(config, sqlite_output)

    for type in config.types.keys():
        process_type(config, type, datastore)

    validate_json_schema = JsonSchemaValidator(config, datastore)
    validate_json_schema.go()

    if staticsite_output:
        static_writer = StaticWriter(config, datastore, staticsite_output)
        static_writer.go()

    if temp_dir:
        shutil.rmtree(temp_dir)


def check(source_dir):

    temp_dir = tempfile.mkdtemp()
    sqlite_output = os.path.join(temp_dir, "database.sqlite")

    config = SiteConfig(source_dir)
    config.load_from_file()

    datastore = DataStoreSQLite(config, sqlite_output)

    for type in config.types.keys():
        process_type(config, type, datastore)

    validate_json_schema = JsonSchemaValidator(config, datastore)
    validate_json_schema.go()

    had_errors = False

    for type in config.types.keys():
        for error in datastore.get_all_json_schema_validation_errors_generator(type):
            print(
                "TYPE "
                + type
                + " RECORD "
                + error.record_id
                + " HAS VALIDATION ERROR: "
                + error.message
            )
            had_errors = True

    shutil.rmtree(temp_dir)

    if had_errors:
        print("ERRORS OCCURRED- See Above")
        sys.exit(-1)
    else:
        sys.exit(0)
