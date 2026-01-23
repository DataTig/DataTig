from staticpipes.bundle_base import BaseBundle
from staticpipes.jinja2_environment import Jinja2Environment
from staticpipes.pipes.copy_from_secondary_source import PipeCopyFromSecondarySource

from datatig.assets import DIRECTORY as DIRECTORY_ASSETS
from datatig.staticpipes.pipes.datatig_write_frictionless_output import (
    PipeDatatigFrictionless,
)
from datatig.staticpipes.pipes.pygments_css import PipePygmentsCSS
from datatig.staticpipes.pipes.staticsite_api import PipeStaticSiteAPI
from datatig.staticpipes.pipes.staticsite_jinja2 import PipeStaticSiteJinja2
from datatig.staticpipes.pipes.staticsite_sqlite_database import (
    PipeStaticSiteSqliteDatabase,
)
from datatig.templates import DIRECTORY as DIRECTORY_TEMPLATES


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
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/css",
                source_filename="brands.min.css",
                destination_directory="fontawesome-free-6-7-2-web/css",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/css",
                source_filename="fontawesome.min.css",
                destination_directory="fontawesome-free-6-7-2-web/css",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/css",
                source_filename="solid.min.css",
                destination_directory="fontawesome-free-6-7-2-web/css",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/webfonts",
                source_filename="fa-brands-400.ttf",
                destination_directory="fontawesome-free-6-7-2-web/webfonts",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/webfonts",
                source_filename="fa-brands-400.woff2",
                destination_directory="fontawesome-free-6-7-2-web/webfonts",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/webfonts",
                source_filename="fa-solid-900.ttf",
                destination_directory="fontawesome-free-6-7-2-web/webfonts",
            ),
            PipeCopyFromSecondarySource(
                secondary_source_name="bundle_datatig_staticsite_assets",
                source_directory="all/fontawesome-free-6-7-2-web/webfonts",
                source_filename="fa-solid-900.woff2",
                destination_directory="fontawesome-free-6-7-2-web/webfonts",
            ),
            PipeDatatigFrictionless(),
            PipePygmentsCSS(),
            PipeStaticSiteJinja2(jinja2_environment=jinja2_environment),
            PipeStaticSiteSqliteDatabase(),
            PipeStaticSiteAPI(),
        ]
        self._secondary_source_directory_paths: dict = {
            "bundle_datatig_staticsite_assets": DIRECTORY_ASSETS,
            "bundle_datatig_staticsite_templates": DIRECTORY_TEMPLATES,
        }
