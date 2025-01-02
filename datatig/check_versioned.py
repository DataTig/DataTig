import os
import sys
import tempfile

from .process import versioned_build
from .sqliteversioned import DataStoreSQLiteVersioned


def check_versioned():
    source_dir = sys.argv[1]
    default_branch = sys.argv[2]
    check_branch = sys.argv[3]

    temp_dir = tempfile.mkdtemp()
    sqlite_output = os.path.join(temp_dir, "database.sqlite")

    versioned_build(
        source_dir=source_dir,
        sqlite_output=sqlite_output,
        refs=[default_branch, check_branch],
        default_ref=default_branch,
    )

    datastore = DataStoreSQLiteVersioned(sqlite_output)

    if not datastore.is_config_same_between_refs(default_branch, check_branch):
        print("The config has changed and we can't check")
        return

    errors_found = False

    for difference_def in datastore.get_data_differences_between_refs(
        default_branch, check_branch
    ):
        # This will print all errors in items edited or added .....
        if difference_def["action"] != "removed":
            item = datastore.get_item(
                check_branch,
                type_id=difference_def["type_id"],
                record_id=difference_def["record_id"],
            )
            for error in item.get_errors():
                print(
                    "TYPE "
                    + difference_def["type_id"]
                    + " RECORD "
                    + error.get_record_id()
                    + " HAS VALIDATION ERROR: "
                    + error.get_message()
                    + " IN DATA PATH "
                    + error.get_data_path()
                )
                errors_found = True

    if errors_found:
        exit(-1)


if __name__ == "__main__":
    check_versioned()
