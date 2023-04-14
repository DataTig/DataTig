from flask.views import View  # type: ignore

import datatig.localserver.datastore
import datatig.localserver.settings


class BaseView(View):
    def __init__(self, jinja2_env):
        self._jinja2_env = jinja2_env
        self._source_dir = datatig.localserver.settings.SOURCE_DIR
        self._sqlite_output_name = datatig.localserver.settings.SQLITE_FILE_NAME
        self._template_variables = {"site": datatig.localserver.settings.SITE_CONFIG}

    def dispatch_request(self, **kargs):
        with datatig.localserver.datastore.DataStore() as db:
            return self.process(db, **kargs)

    def process(self, datastore: datatig.localserver.datastore.DataStore):
        pass
