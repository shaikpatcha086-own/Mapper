"""
===========================================================
Matcher
D365 Metadata Mapper V3
===========================================================
"""

from scorer import Scorer
from rules import violates_business_rule
from ranking import RankingEngine


class Matcher:

    def __init__(self):

        self.scorer = Scorer()

        self.ranking = RankingEngine()

        self.used_source_fields = set()

    # -----------------------------------------------------
    # Match One Target
    # -----------------------------------------------------

    def match_target(
        self,
        target,
        source_metadata
    ):

        candidates = []

        for source in source_metadata:

            # Prevent duplicate mapping
            if source["field"] in self.used_source_fields:
                continue

            # Business rule validation
            if violates_business_rule(
                source["field"],
                target["field"]
            ):
                continue

            result = self.scorer.score(

                source_field=source["field"],

                source_description=source.get(
                    "description", ""
                ),

                target_field=target["field"],

                target_description=target.get(
                    "description", ""
                )

            )

            # Ignore NoMap candidates
            if result["confidence"] < 85:
                continue

            candidates.append({

                "source_field": source["field"],

                "source_description": source.get(
                    "description", ""
                ),

                "target_field": target["field"],

                "target_description": target.get(
                    "description", ""
                ),

                "confidence": result["confidence"],

                "method": result["method"],

                "status": result["status"],

                "reason": result["reason"]

            })

        if not candidates:
            return None

        # -------------------------------------------------
        # Smart Ranking
        # -------------------------------------------------

        best = self.ranking.rank(candidates)

        # -------------------------------------------------
        # Ambiguity Detection
        # -------------------------------------------------

        if len(candidates) > 1:

            second = sorted(
                candidates,
                key=lambda x: x["confidence"],
                reverse=True
            )[1]

            if abs(
                best["confidence"]
                - second["confidence"]
            ) <= 2:

                best["status"] = "Review"

                best["reason"] = (
                    "Multiple high-confidence candidates"
                )

        self.used_source_fields.add(
            best["source_field"]
        )

        return best