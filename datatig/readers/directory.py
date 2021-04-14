import json
import os

from datatig.models.record import RecordModel


def process_type(config, type, datastore):
    start_dir = os.path.join(config.source_dir, config.types[type].directory())
    full_sourcedir = os.path.abspath(config.source_dir)
    if config.git_submodule_directory():
        full_sourcedir = os.path.join(full_sourcedir, config.git_submodule_directory())
    for path, subdirs, files in os.walk(start_dir):
        for name in files:
            if name.endswith(".json"):
                full_filename = os.path.abspath(os.path.join(path, name))
                process_file(
                    config,
                    type,
                    full_filename,
                    full_filename[len(full_sourcedir) + 1 :],
                    name[:-5],
                    datastore,
                )


def process_file(
    config, type, filename_absolute, filename_relative_to_git, id, datastore
):
    with open(filename_absolute) as fp:
        data = json.load(fp)

    record = RecordModel()
    record.load_from_json_file(data, filename_relative_to_git)

    datastore.store(type, id, record)
