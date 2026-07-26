"""
===========================================================
Matcher
D365 Metadata Mapper V3
===========================================================
"""

from functools import lru_cache

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
    HEURISTIC_GATE_TOKENS
)


class Matcher:

    def __init__(self):

        self.scorer = Scorer()

        self.ranking = RankingEngine()

        self.used_source_fields = set()

        self.stats = {
            "targets_processed": 0,
            "sources_considered": 0,
            "sources_skipped_used": 0,
            "sources_skipped_rule": 0,
            "sources_skipped_prefilter": 0,
            "pairs_scored": 0,
            "candidates_below_threshold": 0,
            "heuristic_rejected": 0,
            "matches_returned": 0,
            "nomap_returned": 0,
        }

    def _expanded_tokens(self, value):

        return set(_cached_expand_tokens(value))

    def _meaningful_tokens(self, value):

        return self._expanded_tokens(value) - HEURISTIC_GATE_TOKENS

    def _source_key(self, source):

        source_id = source.get("source_id", "")

        if source_id:
            return source_id

        return source.get("field", "")

    def _has_domain_overlap(self, source_field, target_field):

        source_tokens = self._meaningful_tokens(source_field)
        target_tokens = self._meaningful_tokens(target_field)

        return len(source_tokens.intersection(target_tokens)) > 0

    def _has_meaningful_overlap(self, source, target):

        source_field_tokens = self._meaningful_tokens(source.get("field", ""))
        target_field_tokens = self._meaningful_tokens(target.get("field", ""))

        if source_field_tokens.intersection(target_field_tokens):
            return True

        source_desc_tokens = self._meaningful_tokens(source.get("description", ""))
        target_desc_tokens = self._meaningful_tokens(target.get("description", ""))

        if source_desc_tokens.intersection(target_desc_tokens):
            return True

        if source_field_tokens.intersection(target_desc_tokens):
            return True

        if source_desc_tokens.intersection(target_field_tokens):
            return True

        return False

    # -----------------------------------------------------
    # Match One Target
    # -----------------------------------------------------

    def match_target(
        self,
        target,
        source_metadata
    ):

        self.stats["targets_processed"] += 1

        candidates = []

        for source in source_metadata:

            self.stats["sources_considered"] += 1

            source_key = self._source_key(source)

            # Prevent duplicate mapping
            if source_key in self.used_source_fields:
                self.stats["sources_skipped_used"] += 1
                continue

            # Business rule validation
            if violates_business_rule(
                source["field"],
                target["field"]
            ):
                self.stats["sources_skipped_rule"] += 1
                continue

            if not self._has_meaningful_overlap(source, target):
                self.stats["sources_skipped_prefilter"] += 1
                continue

            self.stats["pairs_scored"] += 1

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
                self.stats["candidates_below_threshold"] += 1
                continue

            if result["method"] in HEURISTIC_METHODS:

                if result["confidence"] < REVIEW_HEURISTIC_MIN_CONFIDENCE:
                    self.stats["heuristic_rejected"] += 1
                    continue

                if result["method"] in STRICT_OVERLAP_METHODS:

                    if not self._has_domain_overlap(
                        source["field"],
                        target["field"]
                    ):
                        self.stats["heuristic_rejected"] += 1
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
            self.stats["nomap_returned"] += 1
            return None

        # -------------------------------------------------
        # Smart Ranking
        # -------------------------------------------------

        best = self.ranking.rank(candidates)

        if best["confidence"] >= MIN_CONFIDENCE_SCORE:
            best["status"] = "Auto Accept"
        else:
            best["status"] = "NoMap"

        self.used_source_fields.add(best.get("source_id", best["source_field"]))

        self.stats["matches_returned"] += 1

        return best


@lru_cache(maxsize=8192)
def _cached_expand_tokens(value):

    return tuple(expand_tokens(tokenize(value)))