"""
===========================================================
Enterprise Concept Engine
D365 Metadata Mapper V4
===========================================================

Converts ERP fields into business concepts for semantic
matching.

Example

ClientId

↓

customer
customer identifier
account

WorkerId

↓

worker
employee
worker identifier

InvoiceAccount

↓

invoice
account
customer
"""

from normalizer import (
    normalize,
    tokenize
)

from abbreviation_expander import (
    expand_field
)

from d365_dictionary import (
    get_business_concept
)

from business_dictionary import (
    expand_tokens
)


class ConceptEngine:

    def __init__(self):

        self.cache = {}

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def get_concepts(self, field_name):

        if not field_name:
            return []

        key = normalize(field_name)

        if key in self.cache:
            return self.cache[key]

        concepts = self._build_concepts(field_name)

        concepts = sorted(set(concepts))

        self.cache[key] = concepts

        return concepts
     # ------------------------------------------------------
    # Build Concepts
    # ------------------------------------------------------

    def _build_concepts(self, field_name):

        concepts = []

        # ---------------------------------------------
        # Original Field
        # ---------------------------------------------

        field = normalize(field_name)

        if field:
            concepts.append(field)

        # ---------------------------------------------
        # Expanded Field
        # ---------------------------------------------

        expanded = expand_field(field_name)

        if expanded:

            concepts.append(expanded)

            expanded_tokens = tokenize(expanded)

            concepts.extend(expanded_tokens)

        # ---------------------------------------------
        # Business Dictionary
        # ---------------------------------------------

        business = get_business_concept(field_name)

        if business:

            concepts.append(normalize(business))

            concepts.extend(

                tokenize(business)

            )

        # ---------------------------------------------
        # Business Synonyms
        # ---------------------------------------------

        concepts = expand_tokens(concepts)

        # ---------------------------------------------
        # Remove Empty Values
        # ---------------------------------------------

        concepts = [

            normalize(x)

            for x in concepts

            if normalize(x)

        ]

        return self._clean(concepts)
    # ------------------------------------------------------
    # Clean Concepts
    # ------------------------------------------------------

    def _clean(self, concepts):

        cleaned = []

        seen = set()

        # Generic concepts that should not dominate matching
        generic_words = {
            "person",
            "organization",
            "party",
            "resource",
            "entity",
            "record",
            "value",
            "data",
            "information",
            "field",
            "code",
            "key",
            "identifier"
        }

        # Keep these generic words only when they are
        # the only available concepts.
        has_business_word = any(
            c not in generic_words
            for c in concepts
        )

        for concept in concepts:

            concept = normalize(concept)

            if not concept:
                continue

            # Remove one-character garbage
            if len(concept) == 1:
                continue

            # Remove duplicates
            if concept in seen:
                continue

            # Remove generic words if we already have
            # stronger business concepts.
            if has_business_word and concept in generic_words:
                continue

            seen.add(concept)
            cleaned.append(concept)

        return cleaned
 # ------------------------------------------------------
# Global Engine
# ------------------------------------------------------

_ENGINE = ConceptEngine()


# ------------------------------------------------------
# Public Function
# ------------------------------------------------------

def get_concepts(field_name):
    """
    Returns a cleaned list of business concepts
    for semantic matching.

    Example:
        WorkerId ->
            ["worker", "employee", "worker identifier"]

        ClientId ->
            ["customer", "client", "customer identifier", "account"]
    """

    return _ENGINE.get_concepts(field_name)              