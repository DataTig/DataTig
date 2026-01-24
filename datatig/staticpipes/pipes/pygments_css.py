import pygments
import pygments.formatters
from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeDataTigPygmentsCSS(BasePipe):

    def __init__(self, output_dir="/", output_filename="pygments.css"):
        self.output_dir = output_dir
        self.output_filename = output_filename

    def start_build(self, current_info: CurrentInfo) -> None:
        self.build_directory.write(
            self.output_dir,
            self.output_filename,
            pygments.formatters.HtmlFormatter().get_style_defs(".highlight"),
        )
