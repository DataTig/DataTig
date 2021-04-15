import os
import tempfile

import pytest

import datatig.process
from datatig.exceptions import DuplicateRecordIdException


def test_json_site():
    # Get Dirs
    source_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "id_clash_site"
    )
    with tempfile.TemporaryDirectory() as staticsite_dir:
        # Process, and test we get exception!
        with pytest.raises(DuplicateRecordIdException):
            datatig.process.go(
                source_dir,
                staticsite_output=staticsite_dir,
            )
