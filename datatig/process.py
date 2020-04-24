from .siteconfig import SiteConfig
from .readers.directory import process_type
from .datastore.memory import DataStoreMemory
from .writers.static import static_writer

def go(source_dir, source_config, out_dir):

    config = SiteConfig(source_dir, out_dir)
    config.load_from_file(source_config)

    datastore = DataStoreMemory(config)

    for type in config.types.keys():
        process_type(config, type, datastore)

    static_writer(config, datastore)
