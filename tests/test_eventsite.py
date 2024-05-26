import json
import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process


def test_event_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "event_site"
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process!
        datatig.process.go(
            source_dir,
            staticsite_output=staticsite_dir,
        )
        # Test Static Site - JSON files
        with open(
            os.path.join(staticsite_dir, "type", "events", "record", "1", "data.json")
        ) as fp:
            one_json = json.load(fp)
            assert {
                "body": "One Event",
                "end": "2023-11-01 11:00:00",
                "start": "2023-11-01 10:00:00",
                "title": "One",
                "submission_deadline": "2023 May 1st",
            } == one_json
        with open(
            os.path.join(staticsite_dir, "type", "events", "record", "2", "data.json")
        ) as fp:
            two_json = json.load(fp)
            assert {
                "end": "2024 Jan 1st 11:00:00",
                "start": "2024 Jan 1st 10:00:00",
                "title": "Two",
                "submission_deadline": "2023-07-15",
            } == two_json
        # Test database
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM type")
                type = cur.fetchone()
                assert "events" == type["id"]
        # Test API
        with open(os.path.join(staticsite_dir, "api.json")) as fp:
            api = json.load(fp)
            assert {
                "description": "The data for a test",
                "title": "Events Site",
                "types": {
                    "events": {
                        "api_url": "/type/events/api.json",
                        "human_url": "/type/events/",
                        "id": "events",
                    }
                },
                "calendars": {
                    "deadlines": {
                        "api_url": "/calendar/deadlines/api.json",
                        "human_url": "/calendar/deadlines/",
                        "id": "deadlines",
                    },
                    "main": {
                        "api_url": "/calendar/main/api.json",
                        "human_url": "/calendar/main/",
                        "id": "main",
                    },
                },
            } == api
        with open(os.path.join(staticsite_dir, "type", "events", "api.json")) as fp:
            type_api = json.load(fp)
            assert {
                "fields": {
                    "title": {"id": "title", "type": "string"},
                    "start": {"id": "start", "type": "datetime"},
                    "end": {"id": "end", "type": "datetime"},
                    "submission_deadline": {
                        "id": "submission_deadline",
                        "type": "date",
                    },
                },
                "id": "events",
                "records_api_url": "/type/events/records_api.json",
            } == type_api

        with open(
            os.path.join(staticsite_dir, "type", "events", "records_api.json")
        ) as fp:
            type_records_api = json.load(fp)
            assert {
                "records": {
                    "1": {
                        "api_url": "/type/events/record/1/api.json",
                        "data_api_url": "/type/events/record/1/data.json",
                        "id": "1",
                    },
                    "2": {
                        "api_url": "/type/events/record/2/api.json",
                        "data_api_url": "/type/events/record/2/data.json",
                        "id": "2",
                    },
                    "3": {
                        "api_url": "/type/events/record/3/api.json",
                        "data_api_url": "/type/events/record/3/data.json",
                        "id": "3",
                    },
                }
            } == type_records_api
        with open(
            os.path.join(staticsite_dir, "type", "events", "record", "1", "api.json")
        ) as fp:
            record_api = json.load(fp)
            assert {"data_api_url": "/type/events/record/1/data.json"} == record_api
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
                field1 = cur.fetchone()
                assert field1["id"] == "title"
                assert field1["sort"] == 1
                field2 = cur.fetchone()
                assert field2["id"] == "start"
                assert field2["sort"] == 2
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_events WHERE id='1'")
                type = cur.fetchone()
                assert "1" == type["id"]
                assert "One" == type["field_title"]
                assert "2023-11-01T10:00:00+01:00" == type["field_start"]
                assert 1698829200 == type["field_start___timestamp"]
                assert "2023-11-01T11:00:00+01:00" == type["field_end"]
                assert 1698832800 == type["field_end___timestamp"]
                assert "2023-05-01" == type["field_submission_deadline"]
                assert 1682935200 == type["field_submission_deadline___timestamp"]
                assert "events/1.md" == type["git_filename"]
                assert "md" == type["format"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_events WHERE id='2'")
                type = cur.fetchone()
                assert "2" == type["id"]
                assert "2024-01-01T10:00:00+01:00" == type["field_start"]
                assert 1704099600 == type["field_start___timestamp"]
                assert "2024-01-01T11:00:00+01:00" == type["field_end"]
                assert 1704103200 == type["field_end___timestamp"]
                assert "2023-07-15" == type["field_submission_deadline"]
                assert 1689415200 == type["field_submission_deadline___timestamp"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM record_events WHERE id='3'")
                type = cur.fetchone()
                assert "3" == type["id"]
                assert "2024-07-01T10:00:00+02:00" == type["field_start"]
                assert 1719820800 == type["field_start___timestamp"]
                assert "2024-07-01T11:00:00+02:00" == type["field_end"]
                assert 1719824400 == type["field_end___timestamp"]
                assert "2024-01-05" == type["field_submission_deadline"]
                assert 1704452400 == type["field_submission_deadline___timestamp"]
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM calendar ORDER BY id ASC")
                calendar1 = cur.fetchone()
                assert "deadlines" == calendar1["id"]
                calendar2 = cur.fetchone()
                assert "main" == calendar2["id"]
            with closing(connection.cursor()) as cur:
                cur.execute(
                    "SELECT * FROM calendar_event WHERE id='deadline_1@example.com'"
                )
                deadline1 = cur.fetchone()
                assert "2023-05-01T12:00:00+02:00" == deadline1["start_iso"]
                assert 1682935200 == deadline1["start_timestamp"]
                assert "2023-05-01T12:00:00+02:00" == deadline1["end_iso"]
                assert 1682935200 == deadline1["end_timestamp"]
                assert "1" == deadline1["record_events___id"]
            with closing(connection.cursor()) as cur:
                cur.execute(
                    "SELECT * FROM calendar_event WHERE id='events_1@example.com'"
                )
                event1 = cur.fetchone()
                assert "2023-11-01T10:00:00+01:00" == event1["start_iso"]
                assert 1698829200 == event1["start_timestamp"]
                assert "2023-11-01T11:00:00+01:00" == event1["end_iso"]
                assert 1698832800 == event1["end_timestamp"]
                assert "1" == deadline1["record_events___id"]
