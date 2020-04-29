import json
import os
import jsonschema

class JsonSchemaValidator:

    def __init__(self, config, datastore):
        self.config = config
        self.datastore = datastore

    def go(self):
        for k, v in self.config.types.items():
            self._validate_type(k, v)

    def _validate_type(self, type_id, type_config):
        if not type_config.json_schema:
            return

        with open(os.path.join(self.config.source_dir, type_config.json_schema())) as fp:
            schema = json.load(fp)

        for item_id in self.datastore.get_ids_in_type(type_id):
            data_item = self.datastore.get_item(type_id, item_id)

            try:
                jsonschema.validate(instance=data_item.data, schema=schema)
                self.datastore.store_json_schema_validation_pass(type_id, item_id)
            except Exception as err:
                err_data = {
                    'message': err.message,
                    'path': err.path,
                    'schema_path': err.schema_path,
                }
                self.datastore.store_json_schema_validation_errors(type_id, item_id, [ err_data ])

