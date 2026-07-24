"""
===========================================================
Matcher
D365 Metadata Mapper V3
===========================================================
"""

from scorer import Scorer
from rules import violates_business_rule
from ranking import RankingEngine
from normalizer import tokenize
from business_dictionary import expand_tokens
from config import (
    MIN_CONFIDENCE_SCORE,
    REVIEW_HEURISTIC_MIN_CONFIDENCE,
    AUTO_ACCEPT_HEURISTIC_MIN_CONFIDENCE,
    DETERMINISTIC_METHODS,
    HEURISTIC_METHODS,
    STRICT_OVERLAP_METHODS,
    GENERIC_MATCH_TOKENS
)


class Matcher:

    def __init__(self):

        self.scorer = Scorer()

        self.ranking = RankingEngine()

        self.used_source_fields = set()

    def _source_key(self, source):

        source_id = source.get("source_id", "")

        if source_id:
            return source_id

        return source.get("field", "")

    def _has_domain_overlap(self, source_field, target_field):

        source_tokens = set(expand_tokens(tokenize(source_field)))
        target_tokens = set(expand_tokens(tokenize(target_field)))

        source_tokens -= GENERIC_MATCH_TOKENS
        target_tokens -= GENERIC_MATCH_TOKENS

        return len(source_tokens.intersection(target_tokens)) > 0

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

            source_key = self._source_key(source)

            # Prevent duplicate mapping
            if source_key in self.used_source_fields:
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
            if result["confidence"] < MIN_CONFIDENCE_SCORE:
                continue

            if result["method"] in HEURISTIC_METHODS:

                if result["confidence"] < REVIEW_HEURISTIC_MIN_CONFIDENCE:
                    continue

                if result["method"] in STRICT_OVERLAP_METHODS:

                    if not self._has_domain_overlap(
                        source["field"],
                        target["field"]
                    ):
                        continue

            candidates.append({

                "source_field": source["field"],

                "source_id": source.get("source_id", source_key),

                "source_entity": source.get("source_entity", ""),

                "source_sheet": source.get("source_sheet", ""),

                "source_file": source.get("source_file", ""),

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

            if (
                best["confidence"] < 100
                and abs(
                    best["confidence"]
                    - second["confidence"]
                ) <= 2
            ):

                best["status"] = "Review"

                best["reason"] = (
                    "Multiple high-confidence candidates"
                )

        if best["method"] in HEURISTIC_METHODS:

            has_overlap = self._has_domain_overlap(
                best["source_field"],
                best["target_field"]
            )

            if (
                has_overlap
                and best["confidence"] >= AUTO_ACCEPT_HEURISTIC_MIN_CONFIDENCE
            ):
                best["status"] = "Auto Accept"

                if best["reason"] == "Multiple high-confidence candidates":
                    best["status"] = "Review"

            else:

                best["status"] = "Review"

                if best["reason"] != "Multiple high-confidence candidates":
                    best["reason"] = (
                        "Heuristic method requires manual review"
                    )

        elif best["method"] not in DETERMINISTIC_METHODS:

            best["status"] = "Review"

        self.used_source_fields.add(best.get("source_id", best["source_field"]))

        return best