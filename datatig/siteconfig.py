import json
import os

import yaml

from .models.type import TypeModel


class SiteConfig:
    def __init__(self, source_dir):
        self.config = {}
        self.types = {}
        self.source_dir = source_dir

    def load_from_file(self):

        if os.path.isfile(os.path.join(self.source_dir, "datatig.json")):
            with open(os.path.join(self.source_dir, "datatig.json")) as fp:
                self.config = json.load(fp)
        elif os.path.isfile(os.path.join(self.source_dir, "datatig.yaml")):
            with open(os.path.join(self.source_dir, "datatig.yaml")) as fp:
                self.config = yaml.safe_load(fp)
        else:
            raise Exception("No Config File!")

        for config in self.config.get("types", []):
            type_config = TypeModel(self)
            type_config.load_from_config(config)
            self.types[type_config.id] = type_config

    def github_url(self):
        return self.config.get("githost", {}).get("url")

    def git_submodule_directory(self):
        return self.config.get("git_submodule_directory")

    def githost_primary_branch(self):
        return self.config.get("githost", {}).get("primary_branch", "main")
