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

        for k,v in self.config.get('types',[]).items():
            self.types[k] = TypeConfig(k, v)

    def github_url(self):
        return self.config.get('github',{}).get('url')

    def github_submodule_directory(self):
        return self.config.get('github',{}).get('submodule_directory')

    def github_primary_branch(self):
        return "master"


class TypeConfig:

    def __init__(self, id, config):
        self.id = id
        self.config = config
        self.fields = {}
        for k, v in config.get('fields',{}).items():
            self.fields[k] = TypeFieldConfig(k, v)

    def directory(self):
        return self.config.get('directory')

    def list_fields(self):
        return self.config.get('list_fields',[]) # TODO add some sensible defaults

class TypeFieldConfig:

    def __init__(self, id, config):
        self.id = id
        self.config = config

    def key(self):
        return self.config.get('key')

    def type(self):
        return self.config.get('type','string')

    def title(self):
        return self.config.get('title',self.id)
