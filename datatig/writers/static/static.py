import os
from typing import Optional

from staticpipes.config import Config
from staticpipes.worker import Worker

from datatig.models.siteconfig import SiteConfigModel
from datatig.sqlite import DataStoreSQLite
from datatig.staticpipes.bundles.staticsite import BundleDataTigStaticSite


class StaticWriter:
    def __init__(
        self,
        config: SiteConfigModel,
        datastore: DataStoreSQLite,
        out_dir: str,
        url: Optional[str] = None,
    ):
        self._config: SiteConfigModel = config
        self._datastore: DataStoreSQLite = datastore
        self._template_variables: dict = {}
        self._out_dir: str = out_dir
        self._url: str = url or ""

    def go(self) -> None:

        worker = Worker(
            Config(
                context={
                    "site": self._config,
                    "url": self._url,
                    "datastore": self._datastore,
                    "datastore_file_size_bytes": os.path.getsize(
                        self._datastore.get_file_name()
                    ),
                    "datatig": {
                        "config": self._config,
                        "datastore": self._datastore,
                        "sqlite_filename": self._datastore.get_file_name(),
                    },
                },
                pipes=[BundleDataTigStaticSite()],
            ),
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "source"),
            self._out_dir,
        )
        worker.build()
