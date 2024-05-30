import os
import sqlite3
import tempfile
from contextlib import closing

import pytest

import datatig.process
from datatig.models.field_list_dictionaries import FieldListDictionariesConfigModel


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
                subrecord = cur.fetchone()
                assert (
                    subrecord["field_who"]
                    == "Anyone who can climb 533 steps. No lift! No Joke!"
                )
                subrecord = cur.fetchone()
                assert subrecord["field_who"] == "18 years of age or younger"
                subrecord = cur.fetchone()
                assert subrecord["field_who"] == "65 years of age or older"


test_different_to_data = [
    ({"l": []}, {"l": []}, False),
    ({"l": [{"title": "cats"}]}, {"l": []}, True),
    ({"l": [{"title": "cats"}]}, {"l": [{"title": "cats"}]}, False),
    ({"l": [{"title": "cats"}]}, {"l": [{"title": "dogs"}]}, True),
]


@pytest.mark.parametrize("data1, data2, expected_result", test_different_to_data)
def test_different_to(data1, data2, expected_result):
    record = None
    field = FieldListDictionariesConfigModel()
    field.load({"id": "l", "key": "l", "fields": [{"id": "title", "key": "title"}]})
    v1 = field.get_value_object(record, data1)
    v2 = field.get_value_object(record, data2)
    assert expected_result == v1.different_to(v2)
