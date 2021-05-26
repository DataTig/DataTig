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
        if not type_config.json_schema():
            return

        with open(
            os.path.join(self.config.source_dir, type_config.json_schema())
        ) as fp:
            schema = json.load(fp)
        schema_version = str(schema.get("$schema", ""))
        if schema_version.startswith("http://json-schema.org/draft-03/schema"):
            schema_validator = jsonschema.Draft3Validator(schema)
        elif schema_version.startswith("http://json-schema.org/draft-04/schema"):
            schema_validator = jsonschema.Draft4Validator(schema)
        elif schema_version.startswith("http://json-schema.org/draft-06/schema"):
            schema_validator = jsonschema.Draft6Validator(schema)
        else:
            schema_validator = jsonschema.Draft7Validator(schema)

        for item_id in self.datastore.get_ids_in_type(type_id):
            data_item = self.datastore.get_item(type_id, item_id)

            errors = sorted(schema_validator.iter_errors(data_item.data), key=str)
            if errors:
                err_data = [
                    {
                        "message": err.message,
                        "path": err.path,
                        "path_str": "/".join(
                            [str(element) for element in list(err.path)]
                        ),
                        "schema_path": err.schema_path,
                        "schema_path_str": "/".join(
                            [str(element) for element in list(err.schema_path)]
                        ),
                    }
                    for err in errors
                ]
                self.datastore.store_json_schema_validation_errors(
                    type_id, item_id, err_data
                )
