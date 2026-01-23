from staticpipes.bundle_base import BaseBundle
from staticpipes.pipes.copy_from_secondary_source import PipeCopyFromSecondarySource

from datatig.assets import DIRECTORY as DIRECTORY_ASSETS
from datatig.templates import DIRECTORY as DIRECTORY_TEMPLATES
from datatig.staticpipes.pipes.datatig_write_frictionless_output import PipeDatatigFrictionless
from datatig.staticpipes.pipes.pygments_css import PipePygmentsCSS
from datatig.staticpipes.pipes.staticsite_root_html import PipeStaticSiteRootHTML
from staticpipes.jinja2_environment import Jinja2Environment

class BundleDataTigStaticSite(BaseBundle):
    """ """

    def __init__(self, jinja2_environment=None):
        super().__init__()
        jinja2_environment = jinja2_environment or Jinja2Environment()
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
            PipeDatatigFrictionless(),
            PipePygmentsCSS(),
            PipeStaticSiteRootHTML(jinja2_environment=jinja2_environment),
        ]
        self._secondary_source_directory_paths: dict = {
            "bundle_datatig_staticsite_assets": DIRECTORY_ASSETS,
            "bundle_datatig_staticsite_templates": DIRECTORY_TEMPLATES
        }
