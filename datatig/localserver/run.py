import sys

import datatig.localserver.app
import datatig.localserver.settings
from datatig.localserver.datastore import DataStore

if __name__ == "__main__":
    datatig.localserver.settings.SOURCE_DIR = sys.argv[1]
    print("Loading Data ...")
    with DataStore() as db:
        db.create(datatig.localserver.settings.SOURCE_DIR)
    print("Running Server ...")
    datatig.localserver.app.app.run(debug=False)
