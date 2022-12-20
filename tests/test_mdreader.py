import json
import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process


def test_md_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "md_site"
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
            assert {
                "title": "One",
                "markdown_body": "A page about 1.",
                "birthday": "2019-09-30",
                "has_cat": True,
                "age": 42.1,
            } == one_json
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "2", "data.json")
        ) as fp:
            two_json = json.load(fp)
            assert {
                "title": 2,
                "markdown_body": "A page about 2.",
                "has_cat": "true",
                "age": "43",
            } == two_json
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "3", "data.json")
        ) as fp:
            three_json = json.load(fp)
            assert {"markdown_body": "A page about 3."} == three_json
        # Test database
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                # Test errors
                cur.execute("SELECT COUNT(*) AS c FROM error")
                error = cur.fetchone()
                assert 0 == error["c"]
                # Test type
                cur.execute("SELECT * FROM type")
                type = cur.fetchone()
                assert "datas" == type["id"]
                # Test a data row
                cur.execute("SELECT * FROM record_datas WHERE id='1'")
                type = cur.fetchone()
                assert "1" == type["id"]
                assert "One" == type["field_title"]
                assert "2019-09-30" == type["field_birthday"]
                assert 1 == type["field_has_cat"]
                assert "datas/1.md" == type["git_filename"]
                assert "md" == type["format"]
                assert 42 == type["field_age"]
                # Test another data row
                cur.execute("SELECT * FROM record_datas WHERE id='2'")
                type = cur.fetchone()
                assert "2" == type["id"]
                assert "2" == type["field_title"]
                assert 43 == type["field_age"]
