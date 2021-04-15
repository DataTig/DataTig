import os
import shutil
import sys
import tempfile

from .readers.directory import process_type
from .siteconfig import SiteConfig
from .sqlite import DataStoreSQLite
from .validate.jsonschema import JsonSchemaValidator
from .writers.static import StaticWriter


def go(
    source_dir,
    staticsite_output=None,
    sqlite_output=None,
    verbose=False,
    check_errors=False,
    check_json_schema_validation_errors=False,
    sys_exit=False,
):

    had_errors = False

    # Config
    config = SiteConfig(source_dir)
    config.load_from_file()

    # SQLite - we always create a SQLite DB. If not requested, we just make it in temp directory and delete after
    temp_dir = None
    if sqlite_output is None:
        temp_dir = tempfile.mkdtemp()
        sqlite_output = os.path.join(temp_dir, "database.sqlite")
    datastore = DataStoreSQLite(config, sqlite_output)

    # Load data
    for type in config.types.keys():
        process_type(config, type, datastore)

    # Validate data
    validate_json_schema = JsonSchemaValidator(config, datastore)
    validate_json_schema.go()

    # Look for errors
    if check_errors:
        for error in datastore.get_all_errors_generator():
            if verbose:
                print("FILENAME " + error.filename + " HAS ERROR: " + error.message)
            had_errors = True

    # Look for validation errors
    if check_json_schema_validation_errors:
        for type in config.types.keys():
            for error in datastore.get_all_json_schema_validation_errors_generator(
                type
            ):
                if verbose:
                    print(
                        "TYPE "
                        + type
                        + " RECORD "
                        + error.record_id
                        + " HAS VALIDATION ERROR: "
                        + error.message
                    )
                had_errors = True

    # Static Site Output
    if staticsite_output:
        static_writer = StaticWriter(config, datastore, staticsite_output)
        static_writer.go()

    # We have now finished - start clearing up

    # Delete temp
    if temp_dir:
        shutil.rmtree(temp_dir)

    # Print final message and exit, if requested
    if had_errors:
        if verbose:
            print("ERRORS OCCURRED- See Above")
        if sys_exit:
            sys.exit(-1)
    else:
        if sys_exit:
            sys.exit(0)
