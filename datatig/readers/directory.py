import json
import os
from typing import Callable, Optional

import yaml

from datatig.models.error import ErrorModel
from datatig.models.record import RecordModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.repository_access import RepositoryAccess

# import traceback


def process_type(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    store_record_callback: Callable,
    store_error_callback: Callable,
) -> None:

    for file_details in repository_access.list_files_in_directory(type.get_directory()):
        try:
            if type.get_record_id_mode() == "directory_and_filename":
                id_material = file_details["path_relative_to_dir"].replace("/", "_")
            else:
                id_material = file_details["name"]
            if file_details["name"].endswith(".json"):
                process_json_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    id_material[:-5],
                    store_record_callback,
                )
            elif file_details["name"].endswith(".yaml"):
                process_yaml_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    id_material[:-5],
                    store_record_callback,
                )
            elif file_details["name"].endswith(".yml"):
                process_yaml_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    id_material[:-4],
                    store_record_callback,
                )
            elif file_details["name"].endswith(".md"):
                process_md_file(
                    config,
                    repository_access,
                    type,
                    os.path.join(
                        type.get_directory(), file_details["path_relative_to_dir"]
                    ),
                    id_material[:-3],
                    store_record_callback,
                )
        except Exception as exception:
            # If debugging, it's sometimes useful to see a stacktrace. Uncomment this print and the import above.
            # But don't check those changes into Git!
            # TODO make this some kind of verbose mode?
            # print(traceback.format_exc())
            store_error_callback(
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
    store_record_callback: Callable,
) -> None:
    data = json.loads(repository_access.get_contents_of_file(filename_relative_to_git))

    record = RecordModel(type=type, id=id)
    record.load_from_json_file(data, filename_relative_to_git)

    store_record_callback(record)


def process_yaml_file(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    filename_relative_to_git: str,
    id,
    store_record_callback: Callable,
) -> None:

    # YAML files can have multiple YAMl documents - load with that in mind.
    data = yaml.safe_load_all(
        repository_access.get_contents_of_file(filename_relative_to_git)
    )
    first_data: dict = next(data, {})
    more_data = next(data, None)
    if more_data:
        # If more data exists error; currently we only support one YAML document per file.
        raise Exception("There was more than one YAML document in this YAML file.")

    # We have our one document - make record, and store
    record = RecordModel(type=type, id=id)
    record.load_from_yaml_file(first_data, filename_relative_to_git)

    store_record_callback(record)


def process_md_file(
    config: SiteConfigModel,
    repository_access: RepositoryAccess,
    type: TypeModel,
    filename_relative_to_git: str,
    id,
    store_record_callback: Callable,
) -> None:
    raw_data = repository_access.get_contents_of_file(filename_relative_to_git)

    markdown_body_is_field: Optional[str] = type.get_markdown_body_is_field()
    if raw_data.startswith("---"):
        bits = raw_data.split("---", 2)
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

    store_record_callback(record)
