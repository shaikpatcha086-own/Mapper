"""
===========================================================
D365 Finance & Operations Metadata Mapper
Version : 3.0
Configuration
===========================================================
"""

# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

APP_NAME = "D365 Finance & Operations Metadata Mapper"
APP_VERSION = "3.0.0"

# ---------------------------------------------------------
# Matching Thresholds
# ---------------------------------------------------------

EXACT_MATCH_SCORE = 100
NORMALIZED_MATCH_SCORE = 99
BUSINESS_MATCH_SCORE = 97
CAMELCASE_MATCH_SCORE = 96
TOKEN_MATCH_SCORE = 94
SOURCE_DESCRIPTION_SCORE = 92
TARGET_DESCRIPTION_SCORE = 90
ABBREVIATION_MATCH_SCORE = 88

FUZZY_MATCH_THRESHOLD = 85
REVIEW_THRESHOLD = 90
AUTO_ACCEPT_THRESHOLD = 95

# ---------------------------------------------------------
# Matching Policy
# ---------------------------------------------------------

MIN_CONFIDENCE_SCORE = 85
HEURISTIC_MIN_CONFIDENCE = 88
REVIEW_HEURISTIC_MIN_CONFIDENCE = 85
AUTO_ACCEPT_HEURISTIC_MIN_CONFIDENCE = 96

DETERMINISTIC_METHODS = {
    "Exact",
    "Normalized",
    "Enterprise Alias",
    "D365 Dictionary",
    "Business Fingerprint"
}

HEURISTIC_METHODS = {
    "Semantic",
    "Fuzzy",
    "Token",
    "Business Token",
    "Business Dictionary",
    "Description",
    "Source Description",
    "Abbreviation",
    "Contains"
}

STRICT_OVERLAP_METHODS = {
    "Semantic",
    "Fuzzy",
    "Contains"
}

GENERIC_MATCH_TOKENS = {
    "id",
    "code",
    "number",
    "name",
    "type",
    "value",
    "data",
    "record",
    "field",
    "key"
}

HEURISTIC_GATE_TOKENS = GENERIC_MATCH_TOKENS.union({

    "group",
    "name",
    "posting",
    "no",
    "num",
    "nbr",
    "identifier",
    "entity"

})

# ---------------------------------------------------------
# Supported Source Header Names
# (Dynamic Detection)
# ---------------------------------------------------------

SOURCE_FIELD_HEADERS = [

    "field",
    "source field",
    "column",
    "column name",
    "attribute",
    "attribute name",
    "name"

]

SOURCE_DESCRIPTION_HEADERS = [

    "description",
    "comments",
    "comment",
    "definition",
    "field description",
    "business description",
    "long description",
    "notes",
    "remark",
    "remarks",
    "explanation"

]

SOURCE_ENTITY_HEADERS = [

    "entity",
    "entity name",
    "table",
    "table name",
    "source entity",
    "source table",
    "data entity"

]

# ---------------------------------------------------------
# Supported Target Header Names
# ---------------------------------------------------------

TARGET_FIELD_HEADERS = [

    "field"

]

TARGET_DESCRIPTION_HEADERS = [

    "field description",
    "description",
    "comments",
    "label"

]

TARGET_DATATYPE_HEADERS = [

    "data type",
    "datatype",
    "type"

]

TARGET_SOURCEFIELD_HEADERS = [

    "source_field",
    "source field"

]

TARGET_MAPPING_ORIGIN_HEADERS = [

    "mapping source",
    "mapped from",
    "mapped from entity",
    "mapping source entity",
    "mapping origin"

]

TARGET_MAPPING_ORIGIN_HEADER_NAME = "Mapping Source"

TARGET_REQUIRED_HEADERS = [

    "fields to be updated",
    "field to be updated",
    "required",
    "mandatory",
    "is required",
    "must map",
    "migration required"

]

# ---------------------------------------------------------
# Normalization
# ---------------------------------------------------------

REMOVE_CHARACTERS = [

    "_",
    "-",
    ".",
    "/",
    "\\",
    "(",
    ")",
    "[",
    "]"

]

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

ENABLE_LOGGING = True

LOG_FOLDER = "logs"

# ---------------------------------------------------------
# AI Assistance Performance Guard
# ---------------------------------------------------------

# Limit how many leftover sources are evaluated for suggestions.
# Increased to 500 to handle large datasets; direct fuzzy matching is fast.
AI_ASSISTANCE_MAX_SOURCES = 500

# Stop AI suggestion pass after this many seconds.
# 120 seconds — LLM is capped at 15 calls so this is sufficient.
AI_ASSISTANCE_TIME_BUDGET_SECONDS = 120.0