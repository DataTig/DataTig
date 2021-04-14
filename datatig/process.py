from .datastore.memory import DataStoreMemory
from .readers.directory import process_type
from .siteconfig import SiteConfig
from .validate.jsonschema import JsonSchemaValidator
from .writers.static import StaticWriter


def go(source_dir, source_config, out_dir):

    config = SiteConfig(source_dir, out_dir)
    config.load_from_file(source_config)

    datastore = DataStoreMemory(config)

    for type in config.types.keys():
        process_type(config, type, datastore)

    validate_json_schema = JsonSchemaValidator(config, datastore)
    validate_json_schema.go()

    static_writer = StaticWriter(config, datastore)
    static_writer.go()
