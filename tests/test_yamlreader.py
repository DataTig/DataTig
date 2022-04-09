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
            assert {
                "title": "One",
                "tags": ["Cats", "Dogs"],
                "birthday": "2019-09-30",
                "has_cat": "true",
            } == one_json
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "2", "data.json")
        ) as fp:
            two_json = json.load(fp)
            assert {"title": "Two", "has_cat": 1} == two_json
        # Test database
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT COUNT(*) AS c FROM error")
                error = cur.fetchone()
                assert 0 == error["c"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM type")
                type = cur.fetchone()
                assert "datas" == type["id"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_datas WHERE id='1'")
                record = cur.fetchone()
                assert "1" == record["id"]
                assert "One" == record["field_title"]
                assert "Cats, Dogs" == record["field_tags"]
                assert "2019-09-30" == record["field_birthday"]
                assert 1 == record["field_has_cat"]
                assert "datas/1.yaml" == record["git_filename"]
                assert "yaml" == record["format"]
            with closing(connection.cursor()) as cur:
                cur.execute(
                    "SELECT * FROM record_datas_field_tags WHERE record_id='1' ORDER BY value"
                )
                field_value = cur.fetchone()
                assert "Cats" == field_value["value"]
                field_value = cur.fetchone()
                assert "Dogs" == field_value["value"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_datas WHERE id='2'")
                record = cur.fetchone()
                assert "2" == record["id"]
                assert "Two" == record["field_title"]
                assert None == record["field_tags"]
                assert 1 == record["field_has_cat"]
                assert "datas/2.yml" == record["git_filename"]
                assert "yaml" == record["format"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_datas WHERE id='3'")
                record = cur.fetchone()
                assert "3" == record["id"]
                assert None == record["field_title"]
                assert None == record["field_tags"]
                assert None == record["field_has_cat"]
                assert "datas/3.yaml" == record["git_filename"]
                assert "yaml" == record["format"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_datas WHERE id='4'")
                record = cur.fetchone()
                assert "4" == record["id"]
                assert "Four" == record["field_title"]
                assert (
                    "This is meant to be a list, we use a string to make sure it doesn't crash."
                    == record["field_tags"]
                )
                assert None == record["field_has_cat"]
                assert "datas/4.yaml" == record["git_filename"]
                assert "yaml" == record["format"]
