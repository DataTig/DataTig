from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeStaticSiteSqliteDatabase(BasePipe):

    def start_build(self, current_info: CurrentInfo) -> None:
        self.build_directory.copy_in_file(
            "/",
            "database.sqlite",
            current_info.get_context("datatig")["sqlite_filename"],
        )
