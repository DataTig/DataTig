import json

import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers.data  # type: ignore

import datatig.localserver.datastore

from .view_base import BaseView


class ViewTypeRecordIndex(BaseView):
    def process(
        self,
        datastore: datatig.localserver.datastore.DataStore,
        type_id=None,
        record_id=None,
    ):

        self._template_variables["type"] = datastore.site_config().get_type(type_id)
        if not self._template_variables["type"]:
            return "404"  # TODO

        self._template_variables["record"] = datastore.database_class().get_item(
            type_id, record_id
        )
        if not self._template_variables["record"]:
            return "404"  # TODO

        self._template_variables["record_data_html"] = pygments.highlight(
            json.dumps(self._template_variables["record"].get_data(), indent=4),
            pygments.lexers.data.JsonLexer(),
            pygments.formatters.HtmlFormatter(),
        )

        return self._jinja2_env.get_template(
            "localserver/type/record/index.html"
        ).render(self._template_variables)
