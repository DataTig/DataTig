import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process


def test_json_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "id_clash_site"
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.go(
            source_dir,
            staticsite_output=staticsite_dir,
        )
        # Check
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM error")
                error = cur.fetchone()
                assert (
                    "The id 1 is duplicated in datas/1.json and datas/1.yaml"
                    == error["message"]
                    or "The id 1 is duplicated in datas/1.yaml and datas/1.json"
                    == error["message"]
                )
                assert error["filename"].endswith("datas/1.json") or error[
                    "filename"
                ].endswith("datas/1.yaml")
