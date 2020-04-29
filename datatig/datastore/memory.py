from datatig.jsondeepreaderwriter import JSONDeepReaderWriter

class DataStoreMemory:

    def __init__(self, site_config):
        self.site_config = site_config
        self.data = {}

    def store(self, type_id, item_id, data):
        if not type_id in self.data.keys():
            self.data[type_id] = {}
        self.data[type_id][item_id] = data

    def store_json_schema_validation_errors(self, type_id, item_id, errors):
        self.data[type_id][item_id].json_schema_validation_errors = errors

    def store_json_schema_validation_pass(self, type_id, item_id):
        self.data[type_id][item_id].json_schema_validation_pass = True

    def get_ids_in_type(self, type_id):
        return sorted(self.data[type_id].keys())

    def get_item(self, type_id, item_id):
        return self.data[type_id][item_id]

    def get_field(self, type_id, item_id, field_id):
        field_config = self.site_config.types[type_id].fields[field_id]
        data = self.data[type_id][item_id].data
        obj = JSONDeepReaderWriter(data)
        return obj.read(field_config.key())

