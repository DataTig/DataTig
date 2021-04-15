import json
import os

import yaml

from datatig.models.error import ErrorModel
from datatig.models.record import RecordModel


def process_type(config, type, datastore):
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
            except Exception as exception:
                error = ErrorModel()
                error.message = str(exception)
                error.filename = full_filename
                datastore.store_error(error)


def process_json_file(
    config, type, filename_absolute, filename_relative_to_git, id, datastore
):
    with open(filename_absolute) as fp:
        data = json.load(fp)

    record = RecordModel()
    record.load_from_json_file(data, filename_relative_to_git)

    datastore.store(type, id, record)


def process_yaml_file(
    config, type, filename_absolute, filename_relative_to_git, id, datastore
):
    with open(filename_absolute) as fp:
        data = yaml.safe_load(fp)

    record = RecordModel()
    record.load_from_yaml_file(data, filename_relative_to_git)

    datastore.store(type, id, record)
