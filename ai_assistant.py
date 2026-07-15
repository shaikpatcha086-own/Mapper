"""
===========================================================
NoMap AI Assistant
D365 Metadata Mapper V3
===========================================================

Provides suggestion candidates only for rows that ended as NoMap
in the main deterministic mapping pass.
"""

from scorer import Scorer
from rules import violates_business_rule


class NoMapAIAssistant:

    def __init__(self, top_n=3):

        self.top_n = top_n

        self.scorer = Scorer()

    def suggest_for_nomap(self, target, source_metadata):
        """
        Return top candidate suggestions for a target field.

        This method is designed for post-processing NoMap rows.
        """

        if not target or not source_metadata:
            return []

        candidates = []

        target_field = target.get("field", "")
        target_description = target.get("description", "")

        for source in source_metadata:

            source_field = source.get("field", "")
            source_description = source.get("description", "")

            if source_field == "":
                continue

            if violates_business_rule(source_field, target_field):
                continue

            result = self.scorer.score(
                source_field=source_field,
                source_description=source_description,
                target_field=target_field,
                target_description=target_description
            )

            if result["confidence"] <= 0:
                continue

            candidates.append({
                "source_field": source_field,
                "source_description": source_description,
                "confidence": result["confidence"],
                "method": result["method"],
                "reason": result["reason"]
            })

        candidates.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        return candidates[:self.top_n]
