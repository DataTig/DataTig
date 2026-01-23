import os.path
import tempfile

from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe

from datatig.writers.static.static import StaticWriter


class PipeDatatigStaticSite(BasePipe):

    def __init__(self, output_dir="/"):
        self.output_dir = output_dir

    def start_build(self, current_info: CurrentInfo) -> None:

        with tempfile.TemporaryDirectory() as tmp_dir_name:

            sw = StaticWriter(
                current_info.get_context("datatig")["config"],
                current_info.get_context("datatig")["datastore"],
                tmp_dir_name,
                (
                    "/" + self.output_dir.strip("/")
                    if self.output_dir and self.output_dir != "/"
                    else ""
                ),
            )
            sw.go()

            for root, dirs, files in os.walk(tmp_dir_name):
                dir = root[len(tmp_dir_name) :]
                for file in files:
                    build_dir = self.output_dir + "/" + dir if self.output_dir else dir
                    build_dir = build_dir.replace("//", "/").strip("/")
                    self.build_directory.copy_in_file(
                        build_dir, file, os.path.join(root, file)
                    )
