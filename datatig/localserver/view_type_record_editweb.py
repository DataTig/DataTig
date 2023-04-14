import json

from flask import redirect, request  # type: ignore

import datatig.localserver.datastore

from .view_base import BaseView


class ViewTypeRecordEditWeb(BaseView):
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

        if request.method == "POST":
            data = json.loads(request.form.get("data"))  # type: ignore
            datastore.update(self._template_variables["record"], data)
            return redirect("/type/" + type_id + "/record/" + record_id)

        return self._jinja2_env.get_template(
            "localserver/type/record/editweb.html"
        ).render(self._template_variables)
