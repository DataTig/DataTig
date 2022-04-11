import os
import sqlite3
import tempfile
from contextlib import closing

import datatig.process

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
            refs_str="59be90b698ae03caf7890827e1fa15af2aa8e9d4,HEAD",
        )
        # Check
        with closing(
            sqlite3.connect(os.path.join(staticsite_dir, "database.sqlite"))
        ) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cur:
                cur.execute("SELECT * FROM git_commit ORDER BY id ASC")
                row = cur.fetchone()
                assert LAST_COMMIT_ID == row["id"]
                row = cur.fetchone()
                assert "59be90b698ae03caf7890827e1fa15af2aa8e9d4" == row["id"]
