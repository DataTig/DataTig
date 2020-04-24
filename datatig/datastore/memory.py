from datatig.jsondeepreaderwriter import JSONDeepReaderWriter

class DataStoreMemory:

    def __init__(self, site_config):
        self.site_config = site_config
        self.data = {}

    def store(self, type_id, item_id, data):
        if not type_id in self.data.keys():
            self.data[type_id] = {}
        self.data[type_id][item_id] = data

    def get_ids_in_type(self, type_id):
        return self.data[type_id].keys()

    def get_item(self, type_id, item_id):
        return self.data[type_id][item_id]

    def get_field(self, type_id, item_id, field_id):
        field_config = self.site_config.types[type_id].fields[field_id]
        data = self.data[type_id][item_id]
        obj = JSONDeepReaderWriter(data)
        return obj.read(field_config.key())

