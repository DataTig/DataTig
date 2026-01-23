from staticpipes.current_info import CurrentInfo
from staticpipes.pipe_base import BasePipe


class PipeStaticSiteJinja2(BasePipe):

    def __init__(self, jinja2_environment=None):
        self._jinja2_environment = jinja2_environment

    def start_build(self, current_info: CurrentInfo) -> None:

        for filename in ["index.html", "errors.html", "robots.txt"]:

            template = self._jinja2_environment.get(
                source_directory=self.source_directory,
                secondary_source_directories=self.secondary_source_directories,
            ).get_template("bundle_datatig_staticsite_templates:static/" + filename)
            contents = template.render(current_info.get_context())
            self.build_directory.write("/", filename, contents)
