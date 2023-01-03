import jsonschema  # type: ignore

from datatig.models.git_commit import GitCommitModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.sqlite import DataStoreSQLite
from datatig.sqliteversioned import DataStoreSQLiteVersioned


class JsonSchemaValidator:
    def __init__(self, config: SiteConfigModel, datastore: DataStoreSQLite):
        self._config = config
        self._datastore = datastore

    def go(self) -> None:
        for type_id, type_config in self._config.get_types().items():
            schema_validator = _json_schema_validator(type_config)

            for item_id in self._datastore.get_ids_in_type(type_id):
                data_item = self._datastore.get_item(type_id, item_id)

                errors = sorted(
                    schema_validator.iter_errors(data_item.get_data()), key=str
                )
                if errors:
                    err_data = [_json_schema_error_to_dict(err) for err in errors]
                    self._datastore.store_json_schema_validation_errors(
                        type_id, item_id, err_data
                    )


class JsonSchemaValidatorVersioned:
    def __init__(
        self,
        config: SiteConfigModel,
        datastore: DataStoreSQLiteVersioned,
        git_commit: GitCommitModel,
    ):
        self._config = config
        self._datastore = datastore
        self._git_commit = git_commit

    def go(self) -> None:
        for type_id, type_config in self._config.get_types().items():
            schema_validator = _json_schema_validator(type_config)

            for item_id in self._datastore.get_ids_in_type(
                self._git_commit.get_commit_hash(), type_id
            ):
                data_item = self._datastore.get_item(
                    self._git_commit.get_commit_hash(), type_id, item_id
                )

                errors = sorted(
                    schema_validator.iter_errors(data_item.get_data()), key=str
                )
                if errors:
                    err_data = [_json_schema_error_to_dict(err) for err in errors]
                    self._datastore.store_json_schema_validation_errors(
                        self._git_commit.get_commit_hash(), type_id, item_id, err_data
                    )


def _json_schema_validator(type_config: TypeModel):
    schema: dict = type_config.get_json_schema_as_dict()
    schema_version = str(schema.get("$schema", ""))
    if schema_version.startswith("http://json-schema.org/draft-03/schema"):
        schema_validator = jsonschema.Draft3Validator(schema)
    elif schema_version.startswith("http://json-schema.org/draft-04/schema"):
        schema_validator = jsonschema.Draft4Validator(schema)
    elif schema_version.startswith("http://json-schema.org/draft-06/schema"):
        schema_validator = jsonschema.Draft6Validator(schema)
    else:
        schema_validator = jsonschema.Draft7Validator(schema)
    return schema_validator


def _json_schema_error_to_dict(err) -> dict:
    return {
        "message": err.message,
        "path": err.path,
        "path_str": "/".join([str(element) for element in list(err.path)]),
        "schema_path": err.schema_path,
        "schema_path_str": "/".join(
            [str(element) for element in list(err.schema_path)]
        ),
    }
