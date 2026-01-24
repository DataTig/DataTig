from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeDataTigStaticSiteSqliteDatabase(BasePipe):

    def __init__(self, output_dir="/"):
        self.output_dir = output_dir

    def start_build(self, current_info: CurrentInfo) -> None:
        self.build_directory.copy_in_file(
            self.output_dir,
            "database.sqlite",
            current_info.get_context("datatig")["sqlite_filename"],
        )
