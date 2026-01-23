from staticpipes.bundle_base import BaseBundle
from staticpipes.pipes.copy_from_secondary_source import PipeCopyFromSecondarySource

from datatig.assets import DIRECTORY as DIRECTORY_ASSETS



class BundleDataTigStaticSite(BaseBundle):
    """ """

    def __init__(self, module_names: list = [], jinja2_environment=None):
        super().__init__()
        self._pipes: list = [
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all",
                source_filename="logo.png",
                destination_directory="/",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all",
                source_filename="main.css",
                destination_directory="/",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="static",
                source_filename="web-edit-or-new.js",
                destination_directory="/",
            ),
        ]
        self._secondary_source_directory_paths: dict = {
            "bundle_datatig_staticsite_assets": DIRECTORY_ASSETS

        }
