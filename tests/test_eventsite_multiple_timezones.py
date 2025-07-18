import os
import sqlite3
import tempfile
from contextlib import closing

import pytest

import datatig.process


@pytest.fixture(scope="module")
def fixture_event_site():
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "data",
        "event_site_multiple_timezones",
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        datatig.process.go(
            source_dir,
            staticsite_output=staticsite_dir,
        )
        yield staticsite_dir


def test_database_errors(fixture_event_site):
    with closing(
        sqlite3.connect(os.path.join(fixture_event_site, "database.sqlite"))
    ) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cur:
            cur.execute("SELECT COUNT(*) AS c FROM error")
            error = cur.fetchone()
            assert 0 == error["c"]


def test_database_event_1(fixture_event_site):
    with closing(
        sqlite3.connect(os.path.join(fixture_event_site, "database.sqlite"))
    ) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_events WHERE id='1'")
            event_data = cur.fetchone()
            assert "1" == event_data["id"]

            assert "2023-07-01T10:00:00+01:00" == event_data["field_start"]
            assert "Europe/London" == event_data["field_start___timezone"]
            assert 1688202000 == event_data["field_start___timestamp"]

            assert "2023-07-01T11:00:00+01:00" == event_data["field_end"]
            assert "Europe/London" == event_data["field_end___timezone"]
            assert 1688205600 == event_data["field_end___timestamp"]


def test_database_event_2(fixture_event_site):
    with closing(
        sqlite3.connect(os.path.join(fixture_event_site, "database.sqlite"))
    ) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_events WHERE id='2'")
            event_data = cur.fetchone()
            assert "2" == event_data["id"]

            assert "2024-01-01T10:00:00-05:00" == event_data["field_start"]
            assert "America/Toronto" == event_data["field_start___timezone"]
            assert 1704121200 == event_data["field_start___timestamp"]

            assert "2024-01-01T11:00:00-05:00" == event_data["field_end"]
            assert "America/Toronto" == event_data["field_end___timezone"]
            assert 1704124800 == event_data["field_end___timestamp"]


def test_database_event_3(fixture_event_site):
    with closing(
        sqlite3.connect(os.path.join(fixture_event_site, "database.sqlite"))
    ) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cur:
            cur.execute("SELECT * FROM record_events WHERE id='3'")
            event_data = cur.fetchone()
            assert "3" == event_data["id"]

            assert "2024-07-01T10:00:00+02:00" == event_data["field_start"]
            assert "Europe/Berlin" == event_data["field_start___timezone"]
            assert 1719820800 == event_data["field_start___timestamp"]

            assert "2024-07-01T11:00:00+02:00" == event_data["field_end"]
            assert "Europe/Berlin" == event_data["field_end___timezone"]
            assert 1719824400 == event_data["field_end___timestamp"]


def test_database_calendar_events_1(fixture_event_site):
    with closing(
        sqlite3.connect(os.path.join(fixture_event_site, "database.sqlite"))
    ) as connection:
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cur:
            cur.execute("SELECT * FROM calendar_event WHERE id='events_1@example.com'")
            event1 = cur.fetchone()
            assert "2023-07-01T10:00:00+01:00" == event1["start_iso"]
            assert 1688202000 == event1["start_timestamp"]
            assert "2023-07-01T11:00:00+01:00" == event1["end_iso"]
            assert 1688205600 == event1["end_timestamp"]
            assert "1" == event1["record_events___id"]
