"""
===========================================================
Business Rules
D365 Metadata Mapper
===========================================================
"""

from normalizer import business_fingerprint


NEGATIVE_RULES = [

    ("customer", "vendor"),
    ("vendor", "customer"),

    ("invoice", "customer"),
    ("customer", "invoice"),

    ("invoice", "vendor"),
    ("vendor", "invoice"),

    ("city", "state"),
    ("state", "city"),

    ("country", "city"),
    ("city", "country"),

    ("postal code", "city"),
    ("city", "postal code"),

    ("quantity", "amount"),
    ("amount", "quantity"),

    ("currency", "language"),
    ("language", "currency"),

    ("email", "employee"),
    ("employee", "email"),

    ("city", "company"),
    ("company", "city"),

    ("city", "chain"),
    ("chain", "city")

]


def violates_business_rule(source_field, target_field):
    """
    Returns True if source and target represent conflicting business concepts.
    """

    source = business_fingerprint(source_field)
    target = business_fingerprint(target_field)

    for source_word, target_word in NEGATIVE_RULES:

        if source_word in source and target_word in target:
            return True

        if target_word in source and source_word in target:
            return True

    return False