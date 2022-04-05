class BuildJSONSchemaResults:
    def __init__(self, json_schema: dict):
        self._json_schema = json_schema

    def get_json_schema(self) -> dict:
        return self._json_schema

    # The reason we have an object with only one data item is that in the future there will be more.
    # It's possible to define fields so you can't build a JSON Schema (keys that clash)
    # and this object will also hold error information.


def build_json_schema(fields: list) -> BuildJSONSchemaResults:
    json_schema: dict = {
        "type": "object",
        "properties": {},
        "$schema": "http://json-schema.org/draft-07/schema",
    }

    for field in fields:
        key_bits = field.get_key().split("/")
        final_key = key_bits.pop()
        json_schema_insert = json_schema
        for key_bit in key_bits:
            if not json_schema_insert["properties"].get(key_bit):
                json_schema_insert["properties"][key_bit] = {
                    "type": "object",
                    "properties": {},
                }
            json_schema_insert = json_schema_insert["properties"][key_bit]
        json_schema_insert["properties"][final_key] = field.get_json_schema()

    return BuildJSONSchemaResults(json_schema)
