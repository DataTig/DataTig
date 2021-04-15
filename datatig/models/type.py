from .type_field import TypeFieldModel


class TypeModel:
    def __init__(self, siteconfig):
        self.id = None
        self.config = None
        self.fields = {}
        self.siteconfig = siteconfig

    def load_from_config(self, config):
        self.id = config.get("id")
        self.config = config
        self.fields = {}
        for config in self.config.get("fields", []):
            field_config = TypeFieldModel()
            field_config.load(config)
            self.fields[field_config.id] = field_config

    def directory(self):
        return self.config.get("directory")

    def directory_in_git_repository(self):
        dir = self.config.get("directory")
        if self.siteconfig.git_submodule_directory() and dir.startswith(
            self.siteconfig.git_submodule_directory()
        ):
            dir = dir[len(self.siteconfig.git_submodule_directory()) :]
        return dir

    def guide_form_xlsx(self):
        return self.config.get("guide_form_xlsx")

    def list_fields(self):
        return self.config.get("list_fields", [])  # TODO add some sensible defaults

    def json_schema(self):
        return self.config.get("json_schema")

    def pretty_json_indent(self):
        return self.config.get("pretty_json_indent", 4)

    def default_format(self):
        return self.config.get("default_format", "yaml")
