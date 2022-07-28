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
        # Check config same
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        assert not datastore.is_config_same_between_refs(
            "f613b6ff02508bb24af0bccd03123293c6264878", "HEAD"
        )


def test_content_edit_only():
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process
        datatig.process.versioned_build(
            SOURCE_DIR,
            sqlite_output=os.path.join(staticsite_dir, "database.sqlite"),
            refs_str="43f044bd87f36bc622097ebcd9a48e617a049373,fdd46cf24487407918e5eac24aee12bbf82b7135",
        )
        # Check config same
        datastore = DataStoreSQLiteVersionedForTesting(
            os.path.join(staticsite_dir, "database.sqlite")
        )
        assert datastore.is_config_same_between_refs(
            "43f044bd87f36bc622097ebcd9a48e617a049373",
            "fdd46cf24487407918e5eac24aee12bbf82b7135",
        )
        # Check list of data differences
        diffs = datastore.get_data_differences_between_refs(
            "43f044bd87f36bc622097ebcd9a48e617a049373",
            "fdd46cf24487407918e5eac24aee12bbf82b7135",
        )
        assert 1 == len(diffs)
        assert "blogs" == diffs[0]["type_id"]
        assert "why-datatig-is-great" == diffs[0]["record_id"]
