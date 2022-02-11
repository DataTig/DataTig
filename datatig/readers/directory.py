import json
import os

import yaml

from datatig.models.error import ErrorModel
from datatig.models.record import RecordModel
from datatig.siteconfig import SiteConfig
from datatig.sqlite import DataStoreSQLite


def process_type(config: SiteConfig, type: str, datastore: DataStoreSQLite) -> None:
    start_dir = os.path.join(config.source_dir, config.types[type].directory())
    full_sourcedir = os.path.abspath(config.source_dir)
    if config.git_submodule_directory():
        full_sourcedir = os.path.join(full_sourcedir, config.git_submodule_directory())
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
                error = ErrorModel()
                error.message = str(exception)
                error.filename = full_filename
                datastore.store_error(error)


def process_json_file(
    config: SiteConfig,
    type: str,
    filename_absolute: str,
    filename_relative_to_git: str,
    id: str,
    datastore: DataStoreSQLite,
) -> None:
    with open(filename_absolute) as fp:
        data = json.load(fp)

    record = RecordModel()
    record.load_from_json_file(data, filename_relative_to_git)

    datastore.store(type, id, record)


def process_yaml_file(
    config: SiteConfig,
    type: str,
    filename_absolute: str,
    filename_relative_to_git: str,
    id,
    datastore: DataStoreSQLite,
) -> None:
    with open(filename_absolute) as fp:
        data = yaml.safe_load(fp)

    record = RecordModel()
    record.load_from_yaml_file(data, filename_relative_to_git)

    datastore.store(type, id, record)


def process_md_file(
    config: SiteConfig,
    type: str,
    filename_absolute: str,
    filename_relative_to_git: str,
    id,
    datastore: DataStoreSQLite,
) -> None:
    with open(filename_absolute) as fp:
        raw_data = fp.read()

    markdown_body_is_field: str = config.types[type].markdown_body_is_field()
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

    record = RecordModel()
    record.load_from_md_file(data, filename_relative_to_git)

    datastore.store(type, id, record)
