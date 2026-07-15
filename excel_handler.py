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

from config import (
    SOURCE_FIELD_HEADERS,
    SOURCE_DESCRIPTION_HEADERS
)

from normalizer import normalize


class SourceMetadataReader:

    def __init__(self, uploaded_file):

        self.uploaded_file = uploaded_file

        self.df = None

        self.field_column = None
        self.description_column = None

    # -----------------------------------------------------
    # Public
    # -----------------------------------------------------

    def load(self):

        filename = self.uploaded_file.name.lower()

        if filename.endswith(".xlsx"):

            self.df = pd.read_excel(
                self.uploaded_file,
                dtype=str
            )

        elif filename.endswith(".csv"):

            self.df = pd.read_csv(
                self.uploaded_file,
                dtype=str
            )

        elif filename.endswith(".txt"):

            self.df = pd.read_csv(
                self.uploaded_file,
                sep=None,
                engine="python",
                dtype=str
            )

        else:

            raise Exception(
                f"Unsupported source file : {filename}"
            )

        self.df = self.df.fillna("")

        self._detect_columns()

    # -----------------------------------------------------
    # Detect Source Columns
    # -----------------------------------------------------

    def _detect_columns(self):

        for column in self.df.columns:

            name = normalize(column)

            if self.field_column is None:

                if name in SOURCE_FIELD_HEADERS:

                    self.field_column = column

            if self.description_column is None:

                if name in SOURCE_DESCRIPTION_HEADERS:

                    self.description_column = column

        # If no field header found

        if self.field_column is None:

            # Assume first column

            self.field_column = self.df.columns[0]

    # -----------------------------------------------------
    # Return Metadata
    # -----------------------------------------------------

    def get_metadata(self):

        metadata = []

        for _, row in self.df.iterrows():

            field = str(
                row[self.field_column]
            ).strip()

            if field == "":
                continue

            if normalize(field) == "field":
                continue

            description = ""

            if self.description_column:

                description = str(
                    row[self.description_column]
                ).strip()

            metadata.append({

                "field": field,

                "description": description

            })

        return metadata

    # -----------------------------------------------------
    # Preview
    # -----------------------------------------------------

    def preview(self):

        return self.df