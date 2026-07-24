"""
===========================================================
Enterprise Scoring Engine
D365 Metadata Mapper V4
===========================================================

Enterprise Intelligent Scoring Engine

Every rule is evaluated.

The highest scoring rule wins.

This prevents early rules from hiding better semantic
matches.
"""

from rapidfuzz import fuzz

from semantic_matcher import semantic_score

from business_dictionary import expand_tokens

from enterprise_alias_dictionary import is_alias_match

from normalizer import (
    normalize,
    tokenize,
    acronym,
    token_similarity,
    contains,
    business_fingerprint,
    fingerprint_tokens
)

from business_dictionary import expand_tokens

from d365_dictionary import get_business_concept

from config import (
    EXACT_MATCH_SCORE,
    NORMALIZED_MATCH_SCORE,
    BUSINESS_MATCH_SCORE,
    CAMELCASE_MATCH_SCORE,
    TOKEN_MATCH_SCORE,
    SOURCE_DESCRIPTION_SCORE,
    TARGET_DESCRIPTION_SCORE,
    ABBREVIATION_MATCH_SCORE,
    FUZZY_MATCH_THRESHOLD
)


class Scorer:

    def score(
        self,
        source_field,
        source_description,
        target_field,
        target_description
    ):

        source_field = source_field or ""
        source_description = source_description or ""
        target_field = target_field or ""
        target_description = target_description or ""
        
        # ==================================================
        # Rule 0
        # Enterprise Alias Match
        # ==================================================

        if is_alias_match(source_field, target_field):

            return self._result(
                100,
                "Enterprise Alias",
                "Matched using Enterprise Alias Dictionary"
            )

        # ---------------------------------------------
        # Best Match Tracker
        # ---------------------------------------------

        best_score = 0
        best_method = "NoMap"
        best_reason = "No suitable match"

        def update(score, method, reason):
            nonlocal best_score
            nonlocal best_method
            nonlocal best_reason

            if score > best_score:
                best_score = score
                best_method = method
                best_reason = reason
        # ==================================================
        # Rule 1
        # Exact Match
        # ==================================================

        if source_field == target_field:

            update(

                EXACT_MATCH_SCORE,

                "Exact",

                "Exact field match"

            )

        # ==================================================
        # Rule 2
        # Normalized Match
        # ==================================================

        if normalize(source_field) == normalize(target_field):

            update(

                NORMALIZED_MATCH_SCORE,

                "Normalized",

                "Normalized field match"

            )

        # ==================================================
        # Rule 3
        # D365 Business Dictionary
        # ==================================================

        source_business = get_business_concept(source_field)

        target_business = get_business_concept(target_field)

        if normalize(source_business) == normalize(target_business):

            update(

                BUSINESS_MATCH_SCORE,

                "D365 Dictionary",

                "Matched using D365 business dictionary"

            )

        # ==================================================
        # Rule 4
        # Business Fingerprint
        # ==================================================

        if business_fingerprint(source_field) == business_fingerprint(target_field):

            update(

                NORMALIZED_MATCH_SCORE,

                "Business Fingerprint",

                "Business concept match"

            )

        # ==================================================
        # Rule 5
        # Business Token Match
        # ==================================================

        source_tokens = fingerprint_tokens(source_field)

        target_tokens = fingerprint_tokens(target_field)

        business_score = token_similarity(

            source_tokens,

            target_tokens

        )

        if business_score >= 1:

            update(

                BUSINESS_MATCH_SCORE,

                "Business Token",

                "Business token similarity"

            )

        # ==================================================
        # Rule 6
        # Business Dictionary Synonyms
        # ==================================================

        source_tokens = expand_tokens(

            tokenize(source_field)

        )

        target_tokens = expand_tokens(

            tokenize(target_field)

        )

        synonym_score = token_similarity(

            source_tokens,

            target_tokens

        )

        if synonym_score >= 1:

            update(

                BUSINESS_MATCH_SCORE,

                "Business Dictionary",

                "Business synonym match"

            )

        expanded_overlap = len(
            set(source_tokens).intersection(target_tokens)
        ) > 0
         # ==================================================
        # Rule 7
        # Contains Match
        # ==================================================

        if contains(source_field, target_field):

            update(

                CAMELCASE_MATCH_SCORE,

                "Contains",

                "Partial field match"

            )

        # ==================================================
        # Rule 8
        # Token Match
        # ==================================================

        token_score = token_similarity(

            tokenize(source_field),

            tokenize(target_field)

        )

        if token_score >= 0.80:

            update(

                TOKEN_MATCH_SCORE,

                "Token",

                "Token similarity"

            )

        # ==================================================
        # Rule 9
        # Acronym Match
        # ==================================================

        source_tokens = tokenize(source_field)
        target_tokens = tokenize(target_field)

        source_acr = acronym(source_field)
        target_acr = acronym(target_field)

        # Acronym matching is meaningful only when both names are
        # multi-token; otherwise single-token values collapse to one
        # letter and create false positives (e.g. City -> CUSTOMERGROUPID).
        if (
            len(source_tokens) >= 2
            and len(target_tokens) >= 2
            and len(source_acr) >= 2
            and source_acr == target_acr
        ):

            update(

                ABBREVIATION_MATCH_SCORE,

                "Abbreviation",

                "Acronym match"

            )

        # ==================================================
        # Rule 10
        # Source Description -> Target Field
        # ==================================================

        if source_description:

            if contains(

                source_description,

                target_field

            ):

                update(

                    SOURCE_DESCRIPTION_SCORE,

                    "Source Description",

                    "Matched using source description"

                )

        # ==================================================
        # Rule 11
        # Source Description -> Target Description
        # ==================================================

        if source_description and target_description:

            description_score = fuzz.token_set_ratio(

                business_fingerprint(source_description),

                business_fingerprint(target_description)

            )

            if description_score >= 90:

                update(

                    TARGET_DESCRIPTION_SCORE,

                    "Description",

                    "Description similarity"

                )

        # Strong deterministic/business matches do not need
        # additional expensive fuzzy/semantic evaluation.
        if best_score >= BUSINESS_MATCH_SCORE:

            return self._result(

                best_score,

                best_method,

                best_reason

            )

        # ==================================================
        # Rule 12
        # Fuzzy Match
        # ==================================================

        if expanded_overlap:

            source_fp = business_fingerprint(source_field)

            target_fp = business_fingerprint(target_field)

            fuzzy_score = max(

                fuzz.ratio(

                    source_fp,

                    target_fp

                ),

                fuzz.partial_ratio(

                    source_fp,

                    target_fp

                ),

                fuzz.token_sort_ratio(

                    source_fp,

                    target_fp

                ),

                fuzz.token_set_ratio(

                    source_fp,

                    target_fp

                )

            )

            if fuzzy_score >= FUZZY_MATCH_THRESHOLD:

                update(

                    round(fuzzy_score),

                    "Fuzzy",

                    "Fuzzy similarity"

                )
            
         # ==================================================
        # Rule 13
        # Semantic Match
        # ==================================================

        semantic = semantic_score(

            source_field,

            target_field

        )

        if semantic > 0:

            update(

                semantic,

                "Semantic",

                "Business concept similarity"

            )

        # ==================================================
        # Final Result
        # ==================================================

        if best_score == 0:

            return self._result(

                0,

                "NoMap",

                "No suitable match"

            )

        return self._result(

            best_score,

            best_method,

            best_reason

        )
     # ======================================================
    # Result Builder
    # ======================================================

    def _result(
        self,
        confidence,
        method,
        reason
    ):

        if confidence >= 95:

            status = "Auto Accept"

        elif confidence >= 85:

            status = "Review"

        else:

            status = "NoMap"

        return {

            "confidence": confidence,

            "method": method,

            "status": status,

            "reason": reason

        }                             