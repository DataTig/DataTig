import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process


def test_tutorial1():
    """This should have a check error"""
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "tutorial1"
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process!
        datatig.process.go(
            source_dir,
            staticsite_output=staticsite_dir,
        )
        # Test database
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_error_shops")
                error = cur.fetchone()
                assert "cathy-cathode" == error["record_id"]
                assert "'url' is a required property" == error["message"]
                assert "" == error["data_path"]
                assert "required" == error["schema_path"]
                assert "jsonschema" == error["generator"]
