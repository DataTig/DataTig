import os
import sqlite3
import tempfile
from contextlib import closing

import pytest

import datatig.process


@pytest.fixture(scope="module")
def fixture_all_field_types_and_options():
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "data",
        "all_field_types_and_options",
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        datatig.process.go(
            source_dir,
            staticsite_output=staticsite_dir,
        )
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                yield cur


def test_record_correct(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='correct' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 0


def test_string_to_short(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='string_to_short' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "string"
    assert errors[0]["message"] == "'D' is too short"


def test_string_to_long(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='string_to_long' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "string"
    assert (
        errors[0]["message"]
        == "'DataTig DataTig DataTig DataTig DataTig DataTig' is too long"
    )


def test_list_string_to_short(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='list_string_to_short' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "list_strings/0"
    assert errors[0]["message"] == "'D' is too short"


def test_list_string_to_long(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='list_string_to_long' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "list_strings/0"
    assert (
        errors[0]["message"]
        == "'DataTig DataTig DataTig DataTig DataTig DataTig' is too long"
    )


def test_list_strings_not_unique(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='list_strings_not_unique' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "list_strings"
    assert errors[0]["message"] == "['DataTig', 'DataTig'] has non-unique elements"


def test_list_dictionaries_not_unique(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='list_dictionaries_not_unique' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "list_dictionaries"
    assert (
        errors[0]["message"]
        == "[{'string': 'DataTig'}, {'string': 'DataTig'}] has non-unique elements"
    )


def test_enum_bad_choice(fixture_all_field_types_and_options):
    res = fixture_all_field_types_and_options.execute(
        "SELECT * FROM record_error_datas WHERE record_id='enum_bad_choice' ORDER BY data_path ASC, message ASC"
    )
    errors = res.fetchall()
    assert len(errors) == 1
    assert errors[0]["data_path"] == "hat"
    assert errors[0]["message"] == "'baseball cap' is not one of ['bowler', 'top']"
