"""
===========================================================
Semantic Matcher
D365 Metadata Mapper V4
===========================================================

Purpose
-------
Compares business concepts instead of raw field names.

Examples

ClientId

↓

customer
organization
party

matches

CustomerAccount


WorkerId

↓

worker
employee
person

matches

EmployeeResponsibleNumber
"""

from concept_engine import get_concepts


class SemanticMatcher:

    def __init__(self):

        pass

    # =====================================================
    # Public
    # =====================================================

    def similarity(
        self,
        source_field,
        target_field
    ):

        source = set(get_concepts(source_field) or [])

        target = set(get_concepts(target_field) or [])

        if not source or not target:

            return 0

        common = source.intersection(target)

        score = len(common) / max(

            len(source),

            len(target)

        )

        return round(score * 100)

    # =====================================================
    # Matching Concepts
    # =====================================================

    def matching_concepts(
        self,
        source_field,
        target_field
    ):

        source = set(get_concepts(source_field) or [])

        target = set(get_concepts(target_field) or [])

        return sorted(

            source.intersection(target)

        )
            # =====================================================
    # Weighted Semantic Similarity
    # =====================================================

    def weighted_similarity(
        self,
        source_field,
        target_field
    ):
        """
        Gives higher weight to important business concepts.
        """

        source = set(get_concepts(source_field) or [])
        target = set(get_concepts(target_field) or [])

        if not source or not target:
            return 0

        common = source.intersection(target)

        # Base score
        score = len(common) * 10

        # Important business concepts
        important = {
            "customer",
            "vendor",
            "employee",
            "worker",
            "organization",
            "party",
            "invoice",
            "project",
            "account",
            "address",
            "payment",
            "identifier"
        }

        # Extra weight for important concepts
        for concept in common:

            if concept in important:
                score += 15
            else:
                score += 5

        return min(score, 100)

    # =====================================================
    # Best Matching Concepts
    # =====================================================

    def best_matches(
        self,
        source_field,
        target_field
    ):

        source = set(get_concepts(source_field) or [])
        target = set(get_concepts(target_field) or [])

        return list(source.intersection(target))
            # =====================================================
    # Explain Match
    # =====================================================

    def explain(
        self,
        source_field,
        target_field
    ):
        """
        Returns a simple explanation of the semantic match.
        """

        common = self.matching_concepts(
            source_field,
            target_field
        )

        score = self.weighted_similarity(
            source_field,
            target_field
        )

        return {

            "score": score,

            "common_concepts": common,

            "source_concepts": sorted(
                get_concepts(source_field)
            ),

            "target_concepts": sorted(
                get_concepts(target_field)
            )

        }


# =====================================================
# Singleton
# =====================================================

_MATCHER = SemanticMatcher()


def semantic_score(
    source_field,
    target_field
):

    return _MATCHER.weighted_similarity(

        source_field,

        target_field

    )


def semantic_matches(
    source_field,
    target_field
):

    return _MATCHER.matching_concepts(

        source_field,

        target_field

    )


def semantic_explain(
    source_field,
    target_field
):

    return _MATCHER.explain(

        source_field,

        target_field

    )