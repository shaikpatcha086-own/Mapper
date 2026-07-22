"""
===========================================================
Workbook Handler
D365 Metadata Mapper V3
===========================================================

Purpose
-------
Reads the target metadata workbook while preserving all
formatting. Only updates the source_field column.
"""

from openpyxl import load_workbook
from copy import copy

from config import (
    TARGET_FIELD_HEADERS,
    TARGET_DESCRIPTION_HEADERS,
    TARGET_SOURCEFIELD_HEADERS,
    TARGET_MAPPING_ORIGIN_HEADERS,
    TARGET_MAPPING_ORIGIN_HEADER_NAME
)

from normalizer import normalize


class WorkbookHandler:

    def __init__(self, uploaded_file):

        uploaded_file.seek(0)

        self.workbook = load_workbook(uploaded_file)

        self.sheet = self.workbook.active

        self.header_row = None

        self.field_col = None
        self.description_col = None
        self.source_field_col = None
        self.mapping_origin_col = None

        self._find_columns()

    # ---------------------------------------------------------
    # Detect Header Row & Columns
    # ---------------------------------------------------------

    def _find_columns(self):

        for row in self.sheet.iter_rows():

            found = False

            for cell in row:

                value = normalize(cell.value)

                if value in TARGET_FIELD_HEADERS:

                    self.header_row = cell.row
                    found = True
                    break

            if found:
                break

        if self.header_row is None:
            raise Exception("Unable to locate Target Field header.")

        for cell in self.sheet[self.header_row]:

            value = normalize(cell.value)

            if value in TARGET_FIELD_HEADERS:

                self.field_col = cell.column

            elif value in TARGET_DESCRIPTION_HEADERS:

                self.description_col = cell.column

            elif value in TARGET_SOURCEFIELD_HEADERS:

                self.source_field_col = cell.column

            elif value in TARGET_MAPPING_ORIGIN_HEADERS:

                self.mapping_origin_col = cell.column

        if self.field_col is None:
            raise Exception("Field column not found.")

        if self.source_field_col is None:
            raise Exception("source_field column not found.")

        if self.mapping_origin_col is None:

            self.mapping_origin_col = self.sheet.max_column + 1

            header_cell = self.sheet.cell(
                row=self.header_row,
                column=self.mapping_origin_col
            )

            header_cell.value = TARGET_MAPPING_ORIGIN_HEADER_NAME

            source_header_cell = self.sheet.cell(
                row=self.header_row,
                column=self.source_field_col
            )

            if source_header_cell.has_style:
                header_cell._style = copy(source_header_cell._style)

            if source_header_cell.number_format:
                header_cell.number_format = source_header_cell.number_format

            if source_header_cell.protection:
                header_cell.protection = copy(source_header_cell.protection)

            if source_header_cell.alignment:
                header_cell.alignment = copy(source_header_cell.alignment)

    # ---------------------------------------------------------
    # Read Target Metadata
    # ---------------------------------------------------------

    def get_target_fields(self):

        metadata = []

        for row in range(self.header_row + 1,
                         self.sheet.max_row + 1):

            field = self.sheet.cell(
                row=row,
                column=self.field_col
            ).value

            if field is None:
                continue

            field = str(field).strip()

            if field == "":
                continue

            description = ""

            if self.description_col:

                value = self.sheet.cell(
                    row=row,
                    column=self.description_col
                ).value

                if value:
                    description = str(value).strip()

            metadata.append({

                "row": row,

                "field": field,

                "description": description

            })

        return metadata

    # ---------------------------------------------------------
    # Update Source Field
    # ---------------------------------------------------------

    def update_source_field(
        self,
        row_number,
        source_field
    ):

        self.sheet.cell(
            row=row_number,
            column=self.source_field_col
        ).value = source_field

    def update_mapping_origin(
        self,
        row_number,
        mapping_origin
    ):

        self.sheet.cell(
            row=row_number,
            column=self.mapping_origin_col
        ).value = mapping_origin

    # ---------------------------------------------------------
    # Save Workbook
    # ---------------------------------------------------------

    def save(self, output_stream):

        self.workbook.save(output_stream)