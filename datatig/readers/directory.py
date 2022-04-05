import json
import os

import yaml

from datatig.models.error import ErrorModel
from datatig.models.record import RecordModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.sqlite import DataStoreSQLite

# import traceback


def process_type(
    config: SiteConfigModel, type: TypeModel, datastore: DataStoreSQLite
) -> None:
    start_dir = os.path.join(config.get_source_dir(), type.get_directory())
    full_sourcedir = os.path.abspath(config.get_source_dir())
    if config.get_git_submodule_directory():
        full_sourcedir = os.path.join(
            full_sourcedir, config.get_git_submodule_directory()
        )
    for path, subdirs, files in os.walk(start_dir):
        for name in files:
            full_filename = os.path.abspath(os.path.join(path, name))
            try:
                if name.endswith(".json"):
                    process_json_file(
                        config,
                        type,
                        full_filename,
                        full_filename[len(full_sourcedir) + 1 :],
                        name[:-5],
                        datastore,
                    )
                elif name.endswith(".yaml"):
                    process_yaml_file(
                        config,
                        type,
                        full_filename,
                        full_filename[len(full_sourcedir) + 1 :],
                        name[:-5],
                        datastore,
                    )
                elif name.endswith(".yml"):
                    process_yaml_file(
                        config,
                        type,
                        full_filename,
                        full_filename[len(full_sourcedir) + 1 :],
                        name[:-4],
                        datastore,
                    )
                elif name.endswith(".md"):
                    process_md_file(
                        config,
                        type,
                        full_filename,
                        full_filename[len(full_sourcedir) + 1 :],
                        name[:-3],
                        datastore,
                    )
            except Exception as exception:
                # If debugging, it's sometimes useful to see a stacktrace. Uncomment this print and the import above.
                # But don't check those changes into Git!
                # TODO make this some kind of verbose mode?
                # print(traceback.format_exc())
                datastore.store_error(
                    ErrorModel(message=str(exception), filename=full_filename)
                )


def process_json_file(
    config: SiteConfigModel,
    type: TypeModel,
    filename_absolute: str,
    filename_relative_to_git: str,
    id: str,
    datastore: DataStoreSQLite,
) -> None:
    with open(filename_absolute) as fp:
        data = json.load(fp)

    record = RecordModel(type=type, id=id)
    record.load_from_json_file(data, filename_relative_to_git)

    datastore.store(record)


def process_yaml_file(
    config: SiteConfigModel,
    type: TypeModel,
    filename_absolute: str,
    filename_relative_to_git: str,
    id,
    datastore: DataStoreSQLite,
) -> None:
    with open(filename_absolute) as fp:
        data = yaml.safe_load(fp)

    record = RecordModel(type=type, id=id)
    record.load_from_yaml_file(data, filename_relative_to_git)

    datastore.store(record)


def process_md_file(
    config: SiteConfigModel,
    type: TypeModel,
    filename_absolute: str,
    filename_relative_to_git: str,
    id,
    datastore: DataStoreSQLite,
) -> None:
    with open(filename_absolute) as fp:
        raw_data = fp.read()

    markdown_body_is_field: str = type.get_markdown_body_is_field()
    if raw_data.startswith("---"):
        bits = raw_data.split("---")
        data = yaml.safe_load(bits[1])
        if markdown_body_is_field:
            data[markdown_body_is_field] = bits[2].strip()
    else:
        if markdown_body_is_field:
            data = {markdown_body_is_field: raw_data.strip()}
        else:
            data = {}

    record = RecordModel(type=type, id=id)
    record.load_from_md_file(data, filename_relative_to_git)

    datastore.store(record)
