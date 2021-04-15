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

    had_errors = False

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

    for error in datastore.get_all_errors_generator():
        print("FILENAME " + error.filename + " HAS ERROR: " + error.message)
        had_errors = True

    # We aren't going to show JSON Schema validation errors here, only in check mode

    if staticsite_output:
        static_writer = StaticWriter(config, datastore, staticsite_output)
        static_writer.go()

    if temp_dir:
        shutil.rmtree(temp_dir)

    if had_errors:
        print("ERRORS OCCURRED- See Above")


def check(source_dir):

    had_errors = False

    temp_dir = tempfile.mkdtemp()
    sqlite_output = os.path.join(temp_dir, "database.sqlite")

    config = SiteConfig(source_dir)
    config.load_from_file()

    datastore = DataStoreSQLite(config, sqlite_output)

    for type in config.types.keys():
        process_type(config, type, datastore)

    validate_json_schema = JsonSchemaValidator(config, datastore)
    validate_json_schema.go()

    for error in datastore.get_all_errors_generator():
        print("FILENAME " + error.filename + " HAS ERROR: " + error.message)
        had_errors = True

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
