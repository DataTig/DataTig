import jinja2
from staticpipes.bundle_base import BaseBundle
from staticpipes.jinja2_environment import Jinja2Environment
from staticpipes.pipes.copy_from_secondary_source import PipeCopyFromSecondarySource
from staticpipes.pipes.process import PipeProcess

from datatig.assets import DIRECTORY as DIRECTORY_ASSETS
from datatig.staticpipes.pipes.datatig_write_frictionless_output import (
    PipeDatatigFrictionless,
)
from datatig.staticpipes.pipes.pygments_css import PipePygmentsCSS
from datatig.staticpipes.pipes.staticsite_api import PipeStaticSiteAPI
from datatig.staticpipes.pipes.staticsite_fullcalendar_io_data import (
    PipeStaticSiteFullCalendarIO,
)
from datatig.staticpipes.pipes.staticsite_jinja2 import PipeStaticSiteJinja2
from datatig.staticpipes.pipes.staticsite_sqlite_database import (
    PipeStaticSiteSqliteDatabase,
)
from datatig.templates import DIRECTORY as DIRECTORY_TEMPLATES

_js_escapes = {
    "\\": "\\u005C",
    "'": "\\u0027",
    '"': "\\u0022",
    ">": "\\u003E",
    "<": "\\u003C",
    "&": "\\u0026",
    "=": "\\u003D",
    "-": "\\u002D",
    ";": "\\u003B",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
# Escape every ASCII character with a value less than 32.
_js_escapes.update(("%c" % z, "\\u%04X" % z) for z in range(32))


def jinja2_escapejs_filter(value: str) -> str:
    retval = []
    for letter in value:
        if letter in _js_escapes:
            retval.append(_js_escapes[letter])
        else:
            retval.append(letter)

    return jinja2.Markup("".join(retval))


class BundleDataTigStaticSite(BaseBundle):
    """ """

    def __init__(self, jinja2_environment=None):
        super().__init__()
        jinja2_environment = jinja2_environment or Jinja2Environment()
        # TODO Adding the filter in like this will only work if
        #  nothing else has already started the environment (like another pipe).
        #  Need to work out something better
        jinja2_environment._filters["escapejs"] = jinja2_escapejs_filter
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
            PipeStaticSiteFullCalendarIO(),
        ]
        self._secondary_source_directory_paths: dict = {
            "bundle_datatig_staticsite_assets": DIRECTORY_ASSETS,
            "bundle_datatig_staticsite_templates": DIRECTORY_TEMPLATES,
        }
