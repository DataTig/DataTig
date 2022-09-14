import os
import tempfile

import datatig.process

from .utils import DataStoreSQLiteVersionedForTesting

LAST_COMMIT_ID = "43f044bd87f36bc622097ebcd9a48e617a049373"

SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data-submodules",
    "site-example-1",
)


def test_first_to_last_commit():
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str="f613b6ff02508bb24af0bccd03123293c6264878,HEAD",
        )
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        # Check config same
        assert not datastore.is_config_same_between_refs(
            "f613b6ff02508bb24af0bccd03123293c6264878", "HEAD"
        )


def test_content_edit_only():
    ref1 = "43f044bd87f36bc622097ebcd9a48e617a049373"
    ref2 = "fdd46cf24487407918e5eac24aee12bbf82b7135"
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str=ref1 + "," + ref2,
        )
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        # Check config same
        assert datastore.is_config_same_between_refs(ref1, ref2)
        # Check list of data differences
        diffs = datastore.get_data_differences_between_refs(ref1, ref2)
        assert 1 == len(diffs)
        assert "blogs" == diffs[0]["type_id"]
        assert "why-datatig-is-great" == diffs[0]["record_id"]
        assert "edited" == diffs[0]["action"]
        # Check field diffs
        record1 = datastore.get_item(ref1, "blogs", "why-datatig-is-great")
        record2 = datastore.get_item(ref2, "blogs", "why-datatig-is-great")
        diff = record1.get_diff(record2)
        assert {"title": {"type": "diff"}} == diff


def test_remove_item():
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str="bbde54437ad70da1a02eda30ccd1627d3a34f782,ed4a308bd1bd9729c2900ae32faf18968242cb1a",
        )
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        # Check config same
        assert datastore.is_config_same_between_refs(
            "bbde54437ad70da1a02eda30ccd1627d3a34f782",
            "ed4a308bd1bd9729c2900ae32faf18968242cb1a",
        )
        # Check list of data differences
        diffs = datastore.get_data_differences_between_refs(
            "bbde54437ad70da1a02eda30ccd1627d3a34f782",
            "ed4a308bd1bd9729c2900ae32faf18968242cb1a",
        )
        assert 1 == len(diffs)
        assert "blogs" == diffs[0]["type_id"]
        assert "why-you-should-really-use-datatig" == diffs[0]["record_id"]
        assert "removed" == diffs[0]["action"]


def test_add_item():
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str="f613b6ff02508bb24af0bccd03123293c6264878,e5f4317282c84225c0f404822d84e8736264d5b5",
        )
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        # Check config same
        assert datastore.is_config_same_between_refs(
            "f613b6ff02508bb24af0bccd03123293c6264878",
            "e5f4317282c84225c0f404822d84e8736264d5b5",
        )
        # Check list of data differences
        diffs = datastore.get_data_differences_between_refs(
            "f613b6ff02508bb24af0bccd03123293c6264878",
            "e5f4317282c84225c0f404822d84e8736264d5b5",
        )
        assert 1 == len(diffs)
        assert "blogs" == diffs[0]["type_id"]
        assert "lets-all-talk-about-datatig" == diffs[0]["record_id"]
        assert "added" == diffs[0]["action"]


def test_no_content_or_config_edited():
    """This diff was an edit to the readme - nothing in the content or config"""
    ref1 = "ed4a308bd1bd9729c2900ae32faf18968242cb1a"
    ref2 = "eba00f1c45e89d02340428e8abcf62f5fbd1a391"
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str=ref1 + "," + ref2,
        )
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        # Check config same
        assert datastore.is_config_same_between_refs(ref1, ref2)
        # Check list of data differences
        diffs = datastore.get_data_differences_between_refs(ref1, ref2)
        assert 0 == len(diffs)
        # Check field diffs
        record1 = datastore.get_item(ref1, "blogs", "why-datatig-is-great")
        record2 = datastore.get_item(ref2, "blogs", "why-datatig-is-great")
        diff = record1.get_diff(record2)
        assert {} == diff


def test_add_new_field_and_content():
    ref1 = "258778d477f73be8769c57bdd6c6078bd5d6bf1c"
    ref2 = "04d3ce4cb5cf74348c95243b49952c86c987b11e"
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str=ref1 + "," + ref2,
        )
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        # Check config different
        assert not datastore.is_config_same_between_refs(ref1, ref2)
        # Check list of data differences
        diffs = datastore.get_data_differences_between_refs(ref1, ref2)
        assert 1 == len(diffs)
        assert "blogs" == diffs[0]["type_id"]
        assert "the-downsides-of-datatig" == diffs[0]["record_id"]
        assert "edited" == diffs[0]["action"]
        # Check field diffs
        record1 = datastore.get_item(ref1, "blogs", "the-downsides-of-datatig")
        record2 = datastore.get_item(ref2, "blogs", "the-downsides-of-datatig")
        diff1to2 = record1.get_diff(record2)
        assert {"deleted": {"type": "added"}} == diff1to2
        diff2to1 = record2.get_diff(record1)
        assert {"deleted": {"type": "removed"}} == diff2to1
