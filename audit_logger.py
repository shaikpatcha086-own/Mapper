"""
===========================================================
Audit Logger
D365 Metadata Mapper V3
===========================================================
"""

import pandas as pd


class AuditLogger:

    def __init__(self):

        self.records = []

    # ---------------------------------------------------------
    # Add Record
    # ---------------------------------------------------------

    def add(self, result):

        if result is None:
            return

        self.records.append({

            "Source Field":
                result.get("source_field", ""),

            "Source Description":
                result.get("source_description", ""),

            "Target Field":
                result.get("target_field", ""),

            "Target Description":
                result.get("target_description", ""),

            "Method":
                result.get("method", ""),

            "Confidence":
                result.get("confidence", ""),

            "Status":
                result.get("status", ""),

            "Reason":
                result.get("reason", "")

        })

    # ---------------------------------------------------------
    # DataFrame
    # ---------------------------------------------------------

    def dataframe(self):

        return pd.DataFrame(self.records)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def summary(self):

        total = len(self.records)

        auto = len([
            x for x in self.records
            if x["Status"] == "Auto Accept"
        ])

        review = len([
            x for x in self.records
            if x["Status"] == "Review"
        ])

        nomap = len([
            x for x in self.records
            if x["Status"] == "NoMap"
        ])

        return {

            "Total": total,

            "Auto Accept": auto,

            "Review": review,

            "NoMap": nomap

        }