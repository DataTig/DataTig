import os
import shutil
import sys
import tempfile

from datatig.models.siteconfig import SiteConfigModel

from .readers.directory import process_type
from .repository_access import RepositoryAccess
from .sqlite import DataStoreSQLite
from .validate.jsonschema import JsonSchemaValidator
from .writers.static import StaticWriter


def go(
    source_dir: str,
    staticsite_output: str = None,
    staticsite_url: str = None,
    sqlite_output: str = None,
    verbose: bool = False,
    check_errors: bool = False,
    check_record_errors: bool = False,
    sys_exit: bool = False,
) -> None:

    had_errors = False

    # Config
    config = SiteConfigModel(source_dir)
    config.load_from_file()

    # SQLite - we always create a SQLite DB. If not requested, we just make it in temp directory and delete after
    temp_dir = None
    if sqlite_output is None:
        temp_dir = tempfile.mkdtemp()
        sqlite_output = os.path.join(temp_dir, "database.sqlite")
    datastore = DataStoreSQLite(config, sqlite_output)

    # Repository Access
    repository_access = RepositoryAccess(source_dir)

    # Load data
    for type in config.get_types().values():
        process_type(
            config,
            repository_access,
            type,
            datastore,
        )

    # Validate data
    validate_json_schema = JsonSchemaValidator(config, datastore)
    validate_json_schema.go()

    # Look for errors
    if check_errors:
        for error in datastore.get_all_errors_generator():
            if verbose:
                print(
                    "FILENAME "
                    + error.get_filename()
                    + " HAS ERROR: "
                    + error.get_message()
                )
            had_errors = True

    # Look for validation errors
    if check_record_errors:
        for type in config.get_types().keys():
            for error in datastore.get_all_record_errors_generator_in_type(type):
                if verbose:
                    print(
                        "TYPE "
                        + type
                        + " RECORD "
                        + error.get_record_id()
                        + " HAS VALIDATION ERROR: "
                        + error.get_message()
                    )
                had_errors = True

    # Static Site Output
    if staticsite_output:
        static_writer = StaticWriter(
            config, datastore, staticsite_output, url=staticsite_url
        )
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
