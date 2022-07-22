import csv
import io
import json
from zipfile import ZipFile

from datatig.models.field import FieldConfigModel
from datatig.models.siteconfig import SiteConfigModel
from datatig.models.type import TypeModel
from datatig.sqlite import DataStoreSQLite


class FrictionlessWriter:
    def __init__(
        self,
        config: SiteConfigModel,
        datastore: DataStoreSQLite,
        out_file: str,
    ):
        self._config: SiteConfigModel = config
        self._datastore: DataStoreSQLite = datastore
        self._out_file: str = out_file
        self._datapackage_json: dict = {}

    def go(self) -> None:
        with ZipFile(self._out_file, "w") as zipfile:

            self._datapackage_json = {
                # TODO "name": "a-unique-human-readable-and-url-usable-identifier",
                "title": self._config.get_title(),
                "description": self._config.get_description(),
                "resources": [],
            }

            for type_id in self._config.get_types():
                self._go_type(type_id, zipfile)

            zipfile.writestr(
                "datapackage.json",
                json.dumps(self._datapackage_json, indent=4),
            )

    def _go_type(self, type_id, zipfile):
        # Setup
        type = self._config.get_type(type_id)
        resource: dict = {
            "name": type_id,
            "path": "csv/" + type_id + ".csv",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "profile": "tabular-data-resource",
            "fields": [{"name": "id", "title": "Record Id", "type": "string"}],
        }
        csv_header_row: list = ["id"]

        # Loop over fields
        for record_field_id in type.get_fields():
            record_field = type.get_field(record_field_id)
            for data_field in record_field.get_frictionless_csv_field_specifications():
                resource["fields"].append(data_field)
                csv_header_row.append(data_field["name"])

        csv_stream = io.StringIO()
        csv_writer = csv.writer(csv_stream)
        csv_writer.writerow(csv_header_row)

        # Loop over each record
        for record_id in self._datastore.get_ids_in_type(type_id):
            record = self._datastore.get_item(type_id, record_id)
            data_row = [record_id]
            for record_field_id in type.get_fields():
                data_row.extend(
                    record.get_field_value(
                        record_field_id
                    ).get_frictionless_csv_data_values()
                )
            csv_writer.writerow(data_row)

        # Write & save results
        zipfile.writestr(resource["path"], csv_stream.getvalue())
        self._datapackage_json["resources"].append(resource)

        # Loop over fields, call for each field for extra stuff
        for record_field_id in type.get_fields():
            self._go_type_field(type, record_field_id, zipfile)

    def _go_type_field(self, type, field_id, zipfile):
        record_field: FieldConfigModel = type.get_field(field_id)
        for (
            sub_resource_spec
        ) in record_field.get_frictionless_csv_resource_specifications():
            self._go_type_field_resource_specification(
                type, record_field, sub_resource_spec, zipfile
            )

    def _go_type_field_resource_specification(
        self, type: TypeModel, field: FieldConfigModel, sub_resource_spec: dict, zipfile
    ):
        sub_resource: dict = {
            "name": type.get_id()
            + "_field_"
            + field.get_id()
            + "_"
            + sub_resource_spec["name"],
            "path": "csv/"
            + type.get_id()
            + "_field_"
            + field.get_id()
            + "_"
            + sub_resource_spec["name"]
            + ".csv",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "profile": "tabular-data-resource",
            "fields": [{"name": "id", "title": "Record Id", "type": "string"}],
        }
        sub_resource["fields"].extend(sub_resource_spec["fields"])
        self._datapackage_json["resources"].append(sub_resource)
        csv_header_row: list = ["id"]
        csv_header_row.extend([i["name"] for i in sub_resource_spec["fields"]])

        csv_stream = io.StringIO()
        csv_writer = csv.writer(csv_stream)
        csv_writer.writerow(csv_header_row)

        # Loop over each record
        for record_id in self._datastore.get_ids_in_type(type.get_id()):
            record = self._datastore.get_item(type.get_id(), record_id)
            for data_row in record.get_field_value(
                field.get_id()
            ).get_frictionless_csv_resource_data_values(sub_resource_spec["name"]):
                data_row.insert(0, record_id)
                csv_writer.writerow(data_row)

        # Write & save results
        zipfile.writestr(sub_resource["path"], csv_stream.getvalue())
        self._datapackage_json["resources"].append(sub_resource)
