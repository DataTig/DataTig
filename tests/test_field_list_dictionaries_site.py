import json
import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process
from datatig.models.siteconfig import SiteConfigModel
from datatig.repository_access import RepositoryAccessLocalFiles
from datatig.sqlite import DataStoreSQLite


def test_type_list_dictionaries_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "data",
        "field_list_dictionaries_site",
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
                cur.execute("SELECT COUNT(*) AS c FROM error")
                error = cur.fetchone()
                assert 0 == error["c"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM type_field ORDER BY sort ASC")
                subrecord = cur.fetchone()
                assert subrecord["id"] == "title"
                subrecord = cur.fetchone()
                assert subrecord["id"] == "tickets"
                subrecord = cur.fetchone()
                assert subrecord["id"] == "tickets/title"
                subrecord = cur.fetchone()
                assert subrecord["id"] == "tickets/who"
            with closing(connection.cursor()) as cur:
                cur.execute(
                    "SELECT * FROM record_attraction___field_tickets ORDER BY record_id ASC, sort ASC"
                )
                # a subrecord ...
                subrecord = cur.fetchone()
                assert (
                    subrecord["field_who"]
                    == "Anyone who can climb 533 steps. No lift! No Joke!"
                )
                subrecord_data = json.loads(subrecord["data"])
                assert (
                    subrecord_data["who"]
                    == "Anyone who can climb 533 steps. No lift! No Joke!"
                )
                # next ...
                subrecord = cur.fetchone()
                assert subrecord["field_who"] == "18 years of age or younger"
                subrecord_data = json.loads(subrecord["data"])
                assert subrecord_data["who"] == "18 years of age or younger"
                # next ...
                subrecord = cur.fetchone()
                assert subrecord["field_who"] == "65 years of age or older"
                subrecord_data = json.loads(subrecord["data"])
                assert subrecord_data["who"] == "65 years of age or older"
        # Test API
        with open(
            os.path.join(
                staticsite_dir,
                "type",
                "attraction",
                "record",
                "chocolate_museum",
                "api.json",
            )
        ) as fp:
            record_api = json.load(fp)
            assert 3 == len(record_api["fields"]["tickets"]["values"])
            assert {
                "fields": {
                    "price": {"value": 9},
                    "title": {"value": "Kids"},
                    "url": {"value": "https://example.com/choolate/kids"},
                    "who": {"value": "18 years of age or younger"},
                }
            } == record_api["fields"]["tickets"]["values"][0]
        # TEST OBJECTS
        config = SiteConfigModel(source_dir)
        config.load_from_file(RepositoryAccessLocalFiles(source_dir))
        db = DataStoreSQLite(config, os.path.join(staticsite_dir, "database.sqlite"))
        # test get_urls_in_values()
        record = db.get_item("attraction", "chocolate_museum")
        assert [
            "https://example.com/choolate/kids",
            "https://example.com/choolate/biggest_kids",
            "https://example.com/choolate/big_kids",
        ] == record.get_urls_in_field_values()
