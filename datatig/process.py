import os
import shutil
import sys
import tempfile
from typing import Optional

from datatig.models.siteconfig import SiteConfigModel

from .exceptions import SiteConfigurationException, SiteConfigurationNotFoundException
from .readers.directory import process_type
from .repository_access import RepositoryAccessLocalFiles, RepositoryAccessLocalGit
from .sqlite import DataStoreSQLite
from .sqliteversioned import DataStoreSQLiteVersioned
from .validate.jsonschema import JsonSchemaValidator, JsonSchemaValidatorVersioned
from .writers.frictionless.frictionless import FrictionlessWriter
from .writers.static.static import StaticWriter
from .writers.staticversioned.staticversioned import StaticVersionedWriter


def go(
    source_dir: str,
    staticsite_output: Optional[str] = None,
    staticsite_url: Optional[str] = None,
    sqlite_output: Optional[str] = None,
    frictionless_output: Optional[str] = None,
    verbose: bool = False,
    check_errors: bool = False,
    check_record_errors: bool = False,
    sys_exit_on_error: bool = False,
) -> None:

    errors_count = 0

    # Repository Access
    repository_access = RepositoryAccessLocalFiles(source_dir)

    # Config
    config = SiteConfigModel(source_dir)
    config.load_from_file(repository_access)

    # SQLite - we always create a SQLite DB. If not requested, we just make it in temp directory and delete after
    temp_dir = None
    if sqlite_output is None:
        temp_dir = tempfile.mkdtemp()
        sqlite_output = os.path.join(temp_dir, "database.sqlite")
    datastore = DataStoreSQLite(config, sqlite_output, error_if_existing_database=True)

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
            errors_count += 1

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
                errors_count += 1

    # Frictionless Output
    if frictionless_output:
        frictionless_writer = FrictionlessWriter(config, datastore, frictionless_output)
        frictionless_writer.go()

    # Static Site Output
    # TODO if frictionless_output is set, should pass it somehow. Otherwise StaticWriter will run it again, which is wastefull.
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
    if errors_count:
        if verbose:
            print("{} ERRORS OCCURRED- See Above".format(errors_count))
        if sys_exit_on_error:
            sys.exit(-1)


def versioned_build(
    source_dir: str,
    staticsite_output: Optional[str] = None,
    staticsite_url: Optional[str] = None,
    sqlite_output: Optional[str] = None,
    refs: list = [],
    refs_str: str = "",
    all_branches: bool = False,
    default_ref: str = "",
    verbose: bool = False,
    check_errors_on_ref: str = "",
    check_errors_on_ref_mode: str = "new",
    sys_exit_on_error: bool = False,
) -> None:

    errors_count = 0

    # Repository Access
    repository_access = RepositoryAccessLocalGit(source_dir)

    # Work out list of refs
    if not refs and refs_str:
        refs = [i for i in refs_str.split(",") if i]
    # Make list unique.
    # Might use something like "main,$BRANCH" in build servers, and then you might get passed "main,main"
    refs = list(set(refs))

    if all_branches:
        for ref in repository_access.list_branches():
            if ref not in refs:
                refs.append(ref)

    # TODO if no refs passed, error

    if default_ref:
        if default_ref not in refs:
            refs.append(default_ref)
    else:
        default_ref = refs[0]

    # SQLite - we always create a SQLite DB. If not requested, we just make it in temp directory and delete after
    temp_dir = None
    if sqlite_output is None:
        temp_dir = tempfile.mkdtemp()
        sqlite_output = os.path.join(temp_dir, "database.sqlite")
    datastore = DataStoreSQLiteVersioned(sqlite_output)

    # For each ref
    for ref in refs:
        try:
            # Set the commit we want, get info
            repository_access.set_ref(ref)
            git_commit = repository_access.get_current_commit()

            # TODO if commit hash is already known to us, don't load data, it is already there
            # (2 branches / refs can point to same commit)

            # Config
            config = SiteConfigModel(source_dir)
            config.load_from_file(repository_access)
            config_id: int = datastore.store_config(config)

            # Save commit
            datastore.store_git_commit(git_commit, config_id)

            # Process data
            for type in config.get_types().values():
                process_type(
                    config,
                    repository_access,
                    type,
                    lambda record: datastore.store_record(git_commit, record),
                    lambda error: datastore.store_error(git_commit, error),
                )

            # Validate data
            validate_json_schema = JsonSchemaValidatorVersioned(
                config, datastore, git_commit
            )
            validate_json_schema.go()
        except (SiteConfigurationNotFoundException, SiteConfigurationException):
            # TODO ideally would put nice message in any output about this.
            # But at least now this doesn't crash whole build process.
            # https://github.com/DataTig/DataTig/issues/27#issuecomment-2304002368
            pass

    # If default ref not one of the refs we found ...
    if not datastore.is_ref_known(default_ref):
        default_ref = refs[0]

    # Check Errors
    if check_errors_on_ref:
        if datastore.is_config_same_between_refs(default_ref, check_errors_on_ref):
            if check_errors_on_ref_mode == "new":
                for error in datastore.get_record_errors_added_between_refs(
                    default_ref, check_errors_on_ref
                ):
                    if verbose:
                        print(
                            "TYPE "
                            + error.get_type_id()
                            + " RECORD "
                            + error.get_record_id()
                            + " HAS VALIDATION ERROR: "
                            + error.get_message()
                            + " IN DATA PATH "
                            + error.get_data_path()
                        )
                    errors_count += 1
                for error in datastore.get_errors_added_between_refs(
                    default_ref, check_errors_on_ref
                ):
                    if verbose:
                        print(
                            "FILENAME {} HAS ERROR: {} ".format(
                                error.get_filename(), error.get_message()
                            )
                        )
                    errors_count += 1
            elif check_errors_on_ref_mode == "all_in_changed_records":
                for difference_def in datastore.get_data_differences_between_refs(
                    default_ref, check_errors_on_ref
                ):
                    if difference_def["action"] != "removed":
                        item = datastore.get_item(
                            check_errors_on_ref,
                            type_id=difference_def["type_id"],
                            record_id=difference_def["record_id"],
                        )
                        for error in item.get_errors():
                            if verbose:
                                print(
                                    "TYPE "
                                    + difference_def["type_id"]
                                    + " RECORD "
                                    + error.get_record_id()
                                    + " HAS VALIDATION ERROR: "
                                    + error.get_message()
                                    + " IN DATA PATH "
                                    + error.get_data_path()
                                )
                            errors_count += 1
                for error in datastore.get_errors_added_between_refs(
                    default_ref, check_errors_on_ref
                ):
                    if verbose:
                        print(
                            "FILENAME {} HAS ERROR: {} ".format(
                                error.get_filename(), error.get_message()
                            )
                        )
                    errors_count += 1
            else:
                raise Exception("UNKNOWN MODE!")
        else:
            pass  # TODO

    # Static Site Output
    if staticsite_output:
        static_writer = StaticVersionedWriter(
            datastore, staticsite_output, url=staticsite_url, default_ref=default_ref
        )
        static_writer.go()

    # Delete temp
    if temp_dir:
        shutil.rmtree(temp_dir)

    # Print final message and exit, if requested
    if errors_count:
        if verbose:
            print("{} ERRORS OCCURRED- See Above".format(errors_count))
        if sys_exit_on_error:
            sys.exit(-1)
