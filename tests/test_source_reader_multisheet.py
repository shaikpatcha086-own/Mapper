import unittest
from io import BytesIO

import pandas as pd

from excel_handler import SourceMetadataReader


class UploadedFileStub:

    def __init__(self, name, payload):
        self.name = name
        self._payload = payload
        self._buffer = BytesIO(payload)

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)

    def tell(self):
        return self._buffer.tell()

    def seekable(self):
        return True

    def readable(self):
        return True


class TestSourceReaderMultiSheet(unittest.TestCase):

    def test_reads_all_sheets_and_entity_column(self):
        output = BytesIO()

        sheet1 = pd.DataFrame([
            {"Field": "CustomerAccount", "Description": "Customer account", "Entity": "CustTable"},
            {"Field": "InvoiceAccount", "Description": "Invoice account", "Entity": "CustInvoiceTable"},
        ])

        sheet2 = pd.DataFrame([
            {"Field": "WorkerId", "Description": "Worker identifier"},
        ])

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet1.to_excel(writer, sheet_name="Customers", index=False)
            sheet2.to_excel(writer, sheet_name="Workers", index=False)

        uploaded = UploadedFileStub("source.xlsx", output.getvalue())

        reader = SourceMetadataReader(uploaded)
        reader.load()

        metadata = reader.get_metadata()

        self.assertEqual(len(metadata), 3)
        self.assertTrue(any(x.get("source_sheet") == "Customers" for x in metadata))
        self.assertTrue(any(x.get("source_sheet") == "Workers" for x in metadata))

        customer = next(x for x in metadata if x["field"] == "CustomerAccount")
        worker = next(x for x in metadata if x["field"] == "WorkerId")

        self.assertEqual(customer.get("source_entity"), "CustTable")
        self.assertEqual(worker.get("source_entity"), "source")
        self.assertTrue(customer.get("source_id"))


if __name__ == "__main__":
    unittest.main()
