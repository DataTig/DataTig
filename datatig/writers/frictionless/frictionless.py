import csv
import io
import json
from zipfile import ZipFile

from datatig.models.siteconfig import SiteConfigModel
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

    def go(self) -> None:
        with ZipFile(self._out_file, "w") as zipfile:

            datapackage_json: dict = {
                # TODO "name": "a-unique-human-readable-and-url-usable-identifier",
                "title": self._config.get_title(),
                "description": self._config.get_description(),
                "resources": [],
            }

            for type_id in self._config.get_types():
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

                for record_field_id in type.get_fields():
                    record_field = type.get_field(record_field_id)
                    for (
                        data_field
                    ) in record_field.get_frictionless_csv_field_specifications():
                        resource["fields"].append(data_field)
                        csv_header_row.append(data_field["name"])

                csv_stream = io.StringIO()
                csv_writer = csv.writer(csv_stream)
                csv_writer.writerow(csv_header_row)

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

                del csv_writer

                zipfile.writestr("csv/" + type.get_id() + ".csv", csv_stream.getvalue())

                datapackage_json["resources"].append(resource)

            zipfile.writestr(
                "datapackage.json",
                json.dumps(datapackage_json, indent=4),
            )
