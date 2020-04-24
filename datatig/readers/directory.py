import os
import json


def process_type(config, type, datastore):
    start_dir = os.path.join(config.source_dir, config.types[type].directory())
    for path, subdirs, files in os.walk(start_dir):
        for name in files:
            process_file(config, type, os.path.join(path, name), name[:-5], datastore)


def process_file(config, type, filename, id, datastore):
    with open(filename) as fp:
        data = json.load(fp)
    datastore.store(type, id, data)

