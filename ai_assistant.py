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
from normalizer import fingerprint_tokens
from config import (
    MIN_CONFIDENCE_SCORE,
    HEURISTIC_MIN_CONFIDENCE,
    DETERMINISTIC_METHODS,
    HEURISTIC_METHODS,
    STRICT_OVERLAP_METHODS,
    GENERIC_MATCH_TOKENS
)


class NoMapAIAssistant:

    def __init__(self, top_n=3):

        self.top_n = top_n

        self.scorer = Scorer()

    def _overlap_metrics(self, source_field, target_field):

        source_tokens = set(fingerprint_tokens(source_field))
        target_tokens = set(fingerprint_tokens(target_field))

        source_tokens -= GENERIC_MATCH_TOKENS
        target_tokens -= GENERIC_MATCH_TOKENS

        overlap = source_tokens.intersection(target_tokens)

        return len(overlap), len(target_tokens)

    def suggest_for_nomap(
        self,
        target,
        source_metadata,
        exclude_sources=None
    ):
        """
        Return top candidate suggestions for a target field.

        This method is designed for post-processing NoMap rows.
        """

        if not target or not source_metadata:
            return []

        excluded = set(exclude_sources or [])

        strict_candidates = []
        fallback_candidates = []

        target_field = target.get("field", "")
        target_description = target.get("description", "")

        for source in source_metadata:

            source_field = source.get("field", "")
            source_description = source.get("description", "")

            if source_field == "":
                continue

            if source_field in excluded:
                continue

            if violates_business_rule(source_field, target_field):
                continue

            result = self.scorer.score(
                source_field=source_field,
                source_description=source_description,
                target_field=target_field,
                target_description=target_description
            )

            if result["confidence"] < 70:
                continue

            overlap_count, target_token_count = self._overlap_metrics(
                source_field,
                target_field
            )

            method = result["method"]

            if method in HEURISTIC_METHODS:

                if result["confidence"] < HEURISTIC_MIN_CONFIDENCE:
                    # Keep weaker heuristic hits as fallback only.
                    fallback_candidates.append({
                        "source_field": source_field,
                        "source_description": source_description,
                        "confidence": result["confidence"],
                        "method": method,
                        "reason": result["reason"],
                        "overlap_count": overlap_count,
                        "deterministic": False
                    })
                    continue

                if method in STRICT_OVERLAP_METHODS and overlap_count == 0:
                    continue

                # Prevent broad fuzzy suggestions for highly specific targets.
                if (
                    method == "Fuzzy"
                    and target_token_count > 1
                    and overlap_count < 2
                ):
                    fallback_candidates.append({
                        "source_field": source_field,
                        "source_description": source_description,
                        "confidence": result["confidence"],
                        "method": method,
                        "reason": result["reason"],
                        "overlap_count": overlap_count,
                        "deterministic": False
                    })
                    continue

                if method == "Abbreviation" and overlap_count == 0:
                    continue

            strict_candidates.append({
                "source_field": source_field,
                "source_description": source_description,
                "confidence": result["confidence"],
                "method": method,
                "reason": result["reason"],
                "overlap_count": overlap_count,
                "deterministic": method in DETERMINISTIC_METHODS
            })

        strict_candidates.sort(
            key=lambda x: (
                x["deterministic"],
                x["confidence"],
                x["overlap_count"]
            ),
            reverse=True
        )

        fallback_candidates.sort(
            key=lambda x: (
                x["confidence"],
                x["overlap_count"]
            ),
            reverse=True
        )

        candidates = strict_candidates

        if not candidates:
            candidates = fallback_candidates

        output = []

        for c in candidates[:self.top_n]:

            output.append({
                "source_field": c["source_field"],
                "source_description": c["source_description"],
                "confidence": c["confidence"],
                "method": c["method"],
                "reason": c["reason"]
            })

        return output
