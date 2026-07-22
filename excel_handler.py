"""
===========================================================
Source Metadata Reader
D365 Metadata Mapper V3
===========================================================

Purpose
-------
Reads any supported source metadata file and returns
a generic metadata structure.

Supported

Excel
CSV
TXT
"""

import pandas as pd
import os

from config import (
    SOURCE_FIELD_HEADERS,
    SOURCE_DESCRIPTION_HEADERS,
    SOURCE_ENTITY_HEADERS
)

from normalizer import normalize


class SourceMetadataReader:

    def __init__(self, uploaded_file):

        self.uploaded_file = uploaded_file

        self.df = None

        self.preview_df = None

        self.metadata = []

        self.field_column = None
        self.description_column = None
        self.entity_column = None

    # -----------------------------------------------------
    # Public
    # -----------------------------------------------------

    def load(self):

        self.uploaded_file.seek(0)

        filename = self.uploaded_file.name.lower()

        self.metadata = []

        if filename.endswith(".xlsx"):

            sheets = pd.read_excel(
                self.uploaded_file,
                dtype=str,
                sheet_name=None
            )

            preview_parts = []

            for sheet_name, sheet_df in sheets.items():

                if sheet_df is None:
                    continue

                sheet_df = sheet_df.fillna("")

                self.metadata.extend(
                    self._extract_metadata(
                        sheet_df,
                        sheet_name=sheet_name
                    )
                )

                preview = sheet_df.copy()
                preview.insert(0, "__source_sheet", str(sheet_name))
                preview_parts.append(preview)

            self.df = next(iter(sheets.values()), pd.DataFrame())

            if preview_parts:
                self.preview_df = pd.concat(preview_parts, ignore_index=True)
            else:
                self.preview_df = pd.DataFrame()

        elif filename.endswith(".csv"):

            self.df = pd.read_csv(
                self.uploaded_file,
                dtype=str
            )

            self.df = self.df.fillna("")
            self.metadata = self._extract_metadata(
                self.df,
                sheet_name=self.uploaded_file.name
            )
            self.preview_df = self.df.copy()

        elif filename.endswith(".txt"):

            self.df = pd.read_csv(
                self.uploaded_file,
                sep=None,
                engine="python",
                dtype=str
            )

            self.df = self.df.fillna("")
            self.metadata = self._extract_metadata(
                self.df,
                sheet_name=self.uploaded_file.name
            )
            self.preview_df = self.df.copy()

        else:

            raise Exception(
                f"Unsupported source file : {filename}"
            )

        if self.df is None:
            self.df = pd.DataFrame()

        if self.preview_df is None:
            self.preview_df = self.df

    # -----------------------------------------------------
    # Detect Source Columns
    # -----------------------------------------------------

    def _detect_columns(self, df):

        field_column = None
        description_column = None
        entity_column = None

        for column in df.columns:

            name = normalize(column)

            if field_column is None:

                if name in SOURCE_FIELD_HEADERS:

                    field_column = column

            if description_column is None:

                if name in SOURCE_DESCRIPTION_HEADERS:

                    description_column = column

            if entity_column is None:

                if name in SOURCE_ENTITY_HEADERS:

                    entity_column = column

        # If no field header found

        if field_column is None:

            # Assume first column

            field_column = df.columns[0]

        self.field_column = field_column
        self.description_column = description_column
        self.entity_column = entity_column

        return field_column, description_column, entity_column

    def _extract_metadata(self, df, sheet_name):

        metadata = []

        if df is None or df.empty:
            return metadata

        field_column, description_column, entity_column = self._detect_columns(df)

        for row_index, row in df.iterrows():

            field = str(
                row[field_column]
            ).strip()

            if field == "":
                continue

            if normalize(field) == "field":
                continue

            description = ""

            if description_column:

                description = str(
                    row[description_column]
                ).strip()

            source_entity = ""

            if entity_column:
                source_entity = str(
                    row[entity_column]
                ).strip()

            source_sheet = str(sheet_name or "")
            source_file = str(self.uploaded_file.name or "")

            if source_entity == "" and source_file:
                source_entity = os.path.splitext(source_file)[0].strip()

            metadata.append({

                "field": field,

                "description": description,

                "source_entity": source_entity,

                "source_sheet": source_sheet,

                "source_file": source_file,

                "source_id": (
                    f"{source_file}::{source_sheet}::{int(row_index) + 1}"
                )

            })

        return metadata

    # -----------------------------------------------------
    # Return Metadata
    # -----------------------------------------------------

    def get_metadata(self):

        return list(self.metadata)

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    def preview(self):

        return self.preview_df