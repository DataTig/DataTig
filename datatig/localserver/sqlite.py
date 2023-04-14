from contextlib import closing

from datatig.models.record import RecordModel
from datatig.sqlite import DataStoreSQLite


class DataStoreSQLiteForLocalServer(DataStoreSQLite):
    def _create(self):
        # When opened via local server, it's already created
        pass

    def store(self, record: RecordModel) -> None:
        # delete all existing data
        with closing(self._connection.cursor()) as cur:
            cur.execute(
                "DELETE FROM record_" + record.get_type().get_id() + "  WHERE id=?",
                [record.get_id()],
            )

            for field in record.get_type().get_fields().values():
                if field.get_type() in ["list-strings"]:
                    cur.execute(
                        """DELETE FROM record_"""
                        + record.get_type().get_id()
                        + """_field_"""
                        + field.get_id()
                        + """ WHERE record_id=? """,
                        [record.get_id()],
                    )

        # Call normal class to store
        super().store(record)
