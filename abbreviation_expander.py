
from abbreviation_dictionary import (
    expand_abbreviation,
    ABBREVIATIONS
)

"""
===========================================================
Abbreviation Expander
D365 Metadata Mapper V4
===========================================================

Purpose
-------
Expands ERP field names into readable business phrases.

Examples
--------
EMPNumb
    -> Employee Number

PAYMENTMthd
    -> Payment Method

INVACCOUNT
    -> Invoice Account

ORG
    -> Organization

The expander prepares field names before they are sent to
the Concept Engine.
"""

import re

from normalizer import normalize
from abbreviation_dictionary import expand_abbreviation


# ==========================================================
# Split Camel Case
# ==========================================================

def split_camel_case(text):
    """
    Example

    CustomerAccount

    →

    Customer Account
    """

    if not text:
        return ""

    return re.sub(

        r'([a-z])([A-Z])',

        r'\1 \2',

        str(text)

    )


# ==========================================================
# Split Numbers
# ==========================================================

def split_numbers(text):
    """
    Example

    Address1Line2

    →

    Address 1 Line 2
    """

    if not text:
        return ""

    text = re.sub(r'([A-Za-z])([0-9])', r'\1 \2', text)

    text = re.sub(r'([0-9])([A-Za-z])', r'\1 \2', text)

    return text


# ==========================================================
# Basic Cleanup
# ==========================================================

def clean_text(text):

    if not text:
        return ""

    text = split_camel_case(text)

    text = split_numbers(text)

    text = text.replace("_", " ")

    text = text.replace("-", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# Expand Tokens
# ==========================================================

def expand_tokens(tokens):
    """
    Expand every token using the abbreviation dictionary.
    """

    expanded = []

    for token in tokens:

        token = normalize(token)

        if token == "":
            continue

        expanded.append(

            expand_abbreviation(token)

        )

    return expanded
# ==========================================================
# Longest Dictionary Match
# ==========================================================

def longest_dictionary_match(text):
    """
    Split compressed ERP words using the abbreviation
    dictionary.

    Example

    EMPNumb

    →

    EMP
    Numb

    →

    employee
    number
    """

    if not text:

        return []

    text = normalize(text)

    text = text.replace(" ", "")

    tokens = []

    position = 0

    dictionary = sorted(

        ABBREVIATIONS.keys(),

        key=len,

        reverse=True

    )

    while position < len(text):

        matched = False

        for word in dictionary:

            if text[position:].startswith(word):

                tokens.append(

                    expand_abbreviation(word)

                )

                position += len(word)

                matched = True

                break

        if not matched:

            tokens.append(

                text[position]

            )

            position += 1

    return tokens

def expand_field(field_name):
    """
    Main API
    """

    if not field_name:

        return ""

    field_name = clean_text(field_name)

    expanded = []

    for token in field_name.split():

        words = longest_dictionary_match(token)

        expanded.extend(words)

    expanded = [

        normalize(x)

        for x in expanded

        if normalize(x)

    ]

    return " ".join(expanded)

# ==========================================================
# Convenience
# ==========================================================

def expand(field_name):

    return expand_field(field_name)