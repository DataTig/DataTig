import json

from .models.type import TypeModel


class SiteConfig:
    def __init__(self, source_dir):
        self.config = {}
        self.types = {}
        self.source_dir = source_dir

    def load_from_file(self, filename):
        with open(filename) as fp:
            self.config = json.load(fp)

        for config in self.config.get("types", []):
            type_config = TypeModel(self)
            type_config.load_from_config(config)
            self.types[type_config.id] = type_config

    def github_url(self):
        return self.config.get("githost", {}).get("url")

    def git_submodule_directory(self):
        return self.config.get("git_submodule_directory")

    def github_primary_branch(self):
        return "master"
