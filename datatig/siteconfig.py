import json


class SiteConfig:

    def __init__(self, source_dir, out_dir):
        self.config = {}
        self.types = {}
        self.source_dir = source_dir
        self.out_dir = out_dir

    def load_from_file(self, filename):
        with open(filename) as fp:
            self.config = json.load(fp)

        for config in self.config.get('types', []):
            type_config = TypeConfig(config, self)
            self.types[type_config.id] = type_config

    def github_url(self):
        return self.config.get('githost',{}).get('url')

    def git_submodule_directory(self):
        return self.config.get('git_submodule_directory')

    def github_primary_branch(self):
        return "master"


class TypeConfig:

    def __init__(self, config, siteconfig):
        self.id = config.get('id')
        self.config = config
        self.fields = {}
        for config in self.config.get('fields', []):
            field_config = TypeFieldConfig(config)
            self.fields[field_config.id] = field_config
        self.siteconfig = siteconfig

    def directory(self):
        return self.config.get('directory')

    def directory_in_git_repository(self):
        dir = self.config.get('directory')
        if self.siteconfig.git_submodule_directory() and dir.startswith(self.siteconfig.git_submodule_directory()):
            dir = dir[len(self.siteconfig.git_submodule_directory()):]
        return dir

    def guide_form_xlsx(self):
        return self.config.get('guide_form_xlsx')

    def list_fields(self):
        return self.config.get('list_fields',[]) # TODO add some sensible defaults

    def json_schema(self):
        return self.config.get('json_schema')

    def pretty_json_indent(self):
        return self.config.get('pretty_json_indent',4)


class TypeFieldConfig:

    def __init__(self, config):
        self.id = config.get('id')
        self.config = config

    def key(self):
        return self.config.get('key')

    def type(self):
        return self.config.get('type','string')

    def title(self):
        return self.config.get('title',self.id)
