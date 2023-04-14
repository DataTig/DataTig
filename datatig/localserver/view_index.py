from .view_base import BaseView


class ViewIndex(BaseView):
    def dispatch_request(self):
        return self._jinja2_env.get_template("localserver/index.html").render(
            self._template_variables
        )
