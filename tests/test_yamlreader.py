import json
import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process


def test_yaml_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "yaml_site"
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process!
        datatig.process.go(
            source_dir,
            staticsite_output=staticsite_dir,
        )
        # Test Static Site - JSON files
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "1", "data.json")
        ) as fp:
            one_json = json.load(fp)
            assert {"title": "One"} == one_json
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "2", "data.json")
        ) as fp:
            two_json = json.load(fp)
            assert {"title": "Two"} == two_json
        # Test database
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM type")
                type = cur.fetchone()
                assert "datas" == type["id"]
