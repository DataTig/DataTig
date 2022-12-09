import json
import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process


def test_json_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "json_site"
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
                "birthday": "2022-10-01",
                "has_cat": True,
                "age": 45,
            } == one_json
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "2", "data.json")
        ) as fp:
            two_json = json.load(fp)
            assert {"title": "Two", "has_cat": False} == two_json
        # Test database
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                # Test type
                cur.execute("SELECT * FROM type")
                type = cur.fetchone()
                assert "datas" == type["id"]
                # Test a data row
                cur.execute("SELECT * FROM record_datas WHERE id='1'")
                type = cur.fetchone()
                assert "1" == type["id"]
                assert "One" == type["field_title"]
                assert "2022-10-01" == type["field_birthday"]
                assert 1 == type["field_has_cat"]
                assert 45 == type["field_age"]
        # Test API
        with open(os.path.join(staticsite_dir, "api.json")) as fp:
            api = json.load(fp)
            assert {
                "description": "The data for a test",
                "title": "Test register",
                "types": {
                    "datas": {
                        "api_url": "/type/datas/api.json",
                        "human_url": "/type/datas/",
                        "id": "datas",
                    }
                },
            } == api
        with open(os.path.join(staticsite_dir, "type", "datas", "api.json")) as fp:
            type_api = json.load(fp)
            assert {
                "fields": {
                    "code": {"id": "code", "type": "string"},
                    "title": {"id": "title", "type": "string"},
                    "tags": {"id": "tags", "type": "list-strings"},
                    "birthday": {"id": "birthday", "type": "date"},
                    "has_cat": {"id": "has_cat", "type": "boolean"},
                    "age": {"id": "age", "type": "integer"},
                },
                "id": "datas",
                "records_api_url": "/type/datas/records_api.json",
            } == type_api

        with open(
            os.path.join(staticsite_dir, "type", "datas", "records_api.json")
        ) as fp:
            type_records_api = json.load(fp)
            assert {
                "records": {
                    "1": {
                        "api_url": "/type/datas/record/1/api.json",
                        "data_api_url": "/type/datas/record/1/data.json",
                        "id": "1",
                    },
                    "2": {
                        "api_url": "/type/datas/record/2/api.json",
                        "data_api_url": "/type/datas/record/2/data.json",
                        "id": "2",
                    },
                    "3": {
                        "api_url": "/type/datas/record/3/api.json",
                        "data_api_url": "/type/datas/record/3/data.json",
                        "id": "3",
                    },
                }
            } == type_records_api
        with open(
            os.path.join(staticsite_dir, "type", "datas", "record", "1", "api.json")
        ) as fp:
            record_api = json.load(fp)
            assert {"data_api_url": "/type/datas/record/1/data.json"} == record_api
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
                cur.execute("SELECT * FROM record_datas WHERE id='1'")
                type = cur.fetchone()
                assert "1" == type["id"]
                assert "One" == type["field_title"]
                assert "2022-10-01" == type["field_birthday"]
                assert 1 == type["field_has_cat"]
                assert "datas/1.json" == type["git_filename"]
                assert "json" == type["format"]
