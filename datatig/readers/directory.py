import json
import os

import yaml

from datatig.models.error import ErrorModel
from datatig.models.record import RecordModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.repository_access import RepositoryAccess
from datatig.sqlite import DataStoreSQLite

# import traceback


def process_type(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    datastore: DataStoreSQLite,
) -> None:
    for file_details in repository_access.list_files_in_directory(type.get_directory()):
        try:
            if file_details["name"].endswith(".json"):
                process_json_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    file_details["name"][:-5],
                    datastore,
                )
            elif file_details["name"].endswith(".yaml"):
                process_yaml_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    file_details["name"][:-5],
                    datastore,
                )
            elif file_details["name"].endswith(".yml"):
                process_yaml_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    file_details["name"][:-4],
                    datastore,
                )
            elif file_details["name"].endswith(".md"):
                process_md_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    file_details["name"][:-3],
                    datastore,
                )
        except Exception as exception:
            # If debugging, it's sometimes useful to see a stacktrace. Uncomment this print and the import above.
            # But don't check those changes into Git!
            # TODO make this some kind of verbose mode?
            # print(traceback.format_exc())
            datastore.store_error(
                ErrorModel(
                    message=str(exception),
                    filename=os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                )
            )


def process_json_file(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    filename_relative_to_git: str,
    id: str,
    datastore: DataStoreSQLite,
) -> None:
    data = json.loads(repository_access.get_contents_of_file(filename_relative_to_git))

    record = RecordModel(type=type, id=id)
    record.load_from_json_file(data, filename_relative_to_git)

    datastore.store(record)


def process_yaml_file(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    filename_relative_to_git: str,
    id,
    datastore: DataStoreSQLite,
) -> None:
    data = yaml.safe_load(
        repository_access.get_contents_of_file(filename_relative_to_git)
    )

    record = RecordModel(type=type, id=id)
    record.load_from_yaml_file(data, filename_relative_to_git)

    datastore.store(record)


def process_md_file(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    filename_relative_to_git: str,
    id,
    datastore: DataStoreSQLite,
) -> None:
    raw_data = repository_access.get_contents_of_file(filename_relative_to_git)

    markdown_body_is_field: str = type.get_markdown_body_is_field()
    if raw_data.startswith("---"):
        bits = raw_data.split("---")
        data = yaml.safe_load(bits[1])
        if markdown_body_is_field:
            data[markdown_body_is_field] = bits[2].strip()
    else:
        if markdown_body_is_field:
            data = {markdown_body_is_field: raw_data.strip()}
        else:
            data = {}

    record = RecordModel(type=type, id=id)
    record.load_from_md_file(data, filename_relative_to_git)

    datastore.store(record)
