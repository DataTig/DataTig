import datatig.localserver.datastore

from .view_base import BaseView


class ViewTypeIndex(BaseView):
    def process(self, datastore: datatig.localserver.datastore.DataStore, type_id=None):

        self._template_variables["datastore"] = datastore.database_class()

        self._template_variables["type"] = datastore.site_config().get_type(type_id)
        if not self._template_variables["type"]:
            return "404"  # TODO

        self._template_variables[
            "records"
        ] = datastore.database_class().get_ids_in_type(type_id)

        return self._jinja2_env.get_template("localserver/type/index.html").render(
            self._template_variables
        )
