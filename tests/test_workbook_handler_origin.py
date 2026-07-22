import unittest
from io import BytesIO

from openpyxl import Workbook

from workbook_handler import WorkbookHandler


class TestWorkbookHandlerMappingOrigin(unittest.TestCase):

    def test_adds_mapping_origin_column_and_updates_value(self):
        wb = Workbook()
        ws = wb.active

        ws.cell(row=1, column=1, value="Field")
        ws.cell(row=1, column=2, value="source_field")
        ws.cell(row=2, column=1, value="CustomerAccount")

        payload = BytesIO()
        wb.save(payload)
        payload.seek(0)

        handler = WorkbookHandler(payload)

        handler.update_source_field(2, "ClientId")
        handler.update_mapping_origin(2, "CustTable")

        self.assertEqual(handler.sheet.cell(row=2, column=2).value, "ClientId")

        origin_header = handler.sheet.cell(row=1, column=3).value
        origin_value = handler.sheet.cell(row=2, column=3).value

        self.assertEqual(origin_header, "Mapping Source")
        self.assertEqual(origin_value, "CustTable")


if __name__ == "__main__":
    unittest.main()
