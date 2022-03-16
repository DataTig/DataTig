class JSONDeepReaderWriter:
    def __init__(self, json: dict):
        self.json = json

    def read(self, path: str, default=None) -> dict:
        path_bits = path.split("/")
        current_json = self.json
        for path_bit in path_bits:
            if path_bit in current_json.keys():
                current_json = current_json[path_bit]
            else:
                return default
        return current_json

    def write(self, path: str, data) -> None:
        path_bits = path.split("/")
        last_path_bit = path_bits.pop()
        current_json = self.json
        for path_bit in path_bits:
            if path_bit not in current_json.keys():
                current_json[path_bit] = {}
            current_json = current_json[path_bit]
        current_json[last_path_bit] = data

    def get_json(self) -> dict:
        return self.json
