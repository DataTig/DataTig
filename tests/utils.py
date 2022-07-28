import sqlite3

from datatig.sqliteversioned import DataStoreSQLiteVersioned


class DataStoreSQLiteVersionedForTesting(DataStoreSQLiteVersioned):
    def __init__(self, out_filename: str):
        self._out_filename: str = out_filename
        self._connection = sqlite3.connect(out_filename)
        self._connection.row_factory = sqlite3.Row
        # Override init so we do NOT create tables, as is usually done.
