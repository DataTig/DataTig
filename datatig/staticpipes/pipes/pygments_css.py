import os.path
import tempfile
import pygments

from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe

from datatig.writers.frictionless.frictionless import FrictionlessWriter


class PipePygmentsCSS(BasePipe):

    def __init__(self, output_dir="/", output_filename="pygments.css"):
        self.output_dir = output_dir
        self.output_filename = output_filename

    def start_build(self, current_info: CurrentInfo) -> None:
        self.build_directory.write(self.output_dir, self.output_filename, pygments.formatters.HtmlFormatter().get_style_defs(".highlight"))
