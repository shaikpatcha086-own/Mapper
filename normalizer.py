"""
===========================================================
Normalization Utilities
D365 Metadata Mapper V3
===========================================================
"""

import re

from config import REMOVE_CHARACTERS


# ---------------------------------------------------------
# Safe String
# ---------------------------------------------------------

def safe_string(value):
    """
    Convert any value into a clean string.
    """

    if value is None:
        return ""

    return str(value).strip()


# ---------------------------------------------------------
# Normalize
# ---------------------------------------------------------

def normalize(value):
    """
    Normalize text for matching.

    Example:
        Customer_Account
        customer-account

        →

        customer account
    """

    value = safe_string(value)

    if value == "":
        return ""

    # CamelCase -> Camel Case
    value = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        value
    )

    value = value.lower()

    for ch in REMOVE_CHARACTERS:
        value = value.replace(ch, " ")

    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ---------------------------------------------------------
# Tokenize
# ---------------------------------------------------------

def tokenize(value):
    """
    Return normalized tokens.
    """

    value = normalize(value)

    if value == "":
        return []

    return value.split()


# ---------------------------------------------------------
# Remove Duplicate Tokens
# ---------------------------------------------------------

def unique_tokens(value):

    return list(dict.fromkeys(tokenize(value)))


# ---------------------------------------------------------
# Acronym
# ---------------------------------------------------------

def acronym(value):
    """
    Customer Account Number

    →

    CAN
    """

    tokens = tokenize(value)

    if len(tokens) == 0:
        return ""

    return "".join(token[0] for token in tokens).upper()


# ---------------------------------------------------------
# Token Similarity
# ---------------------------------------------------------

def token_similarity(tokens1, tokens2):

    if not tokens1 or not tokens2:
        return 0

    common = set(tokens1).intersection(tokens2)

    return len(common) / max(len(tokens1), len(tokens2))


# ---------------------------------------------------------
# Contains
# ---------------------------------------------------------

def contains(value1, value2):
    """
    True if one normalized string contains the other.
    """

    v1 = normalize(value1)
    v2 = normalize(value2)

    if not v1 or not v2:
        return False

    return v1 in v2 or v2 in v1


# ---------------------------------------------------------
# Empty
# ---------------------------------------------------------

def is_empty(value):

    return normalize(value) == ""


# ---------------------------------------------------------
# Business Vocabulary
# ---------------------------------------------------------

BUSINESS_WORDS = {

    # Customer
    "cust": "customer",
    "custaccount": "customer account",
    "custacct": "customer account",

    # Vendor
    "vend": "vendor",
    "vendaccount": "vendor account",

    # Invoice
    "inv": "invoice",
    "invaccount": "invoice account",
    "invoiceacct": "invoice account",

    # Address
    "addr": "address",
    "addr1": "address",
    "addr2": "address",
    "addr3": "address",

    # Account
    "acct": "account",
    "acc": "account",

    # Number
    "num": "number",
    "no": "number",

    # Quantity
    "qty": "quantity",

    # Amount
    "amt": "amount",

    # Description
    "desc": "description",

    # Telephone
    "tel": "telephone",
    "mob": "mobile",

    # Postal Code
    "zip": "postal code",
    "zipcode": "postal code"
}


# ---------------------------------------------------------
# Business Fingerprint
# ---------------------------------------------------------

def business_fingerprint(text):
    """
    Converts business abbreviations into business concepts.
    """

    text = normalize(text)

    if text == "":
        return ""

    tokens = tokenize(text)

    result = []

    for token in tokens:

        if token in BUSINESS_WORDS:
            result.extend(BUSINESS_WORDS[token].split())
        else:
            result.append(token)

    return " ".join(result)


# ---------------------------------------------------------
# Fingerprint Tokens
# ---------------------------------------------------------

def fingerprint_tokens(text):

    return tokenize(
        business_fingerprint(text)
    )