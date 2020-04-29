

class StoredItem:

    def __init__(self, data, git_filename):
        self.data = data
        self.git_filename = git_filename
        self.json_schema_validation_errors = {}
        self.json_schema_validation_pass = False
