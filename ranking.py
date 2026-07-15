"""
===========================================================
Enterprise Ranking Engine
D365 Metadata Mapper V3
===========================================================

Ranks multiple mapping candidates using
weighted business rules.
"""


class RankingEngine:

    # -----------------------------------------------------
    # Rank Candidates
    # -----------------------------------------------------

    def rank(self, candidates):

        if not candidates:
            return None

        for candidate in candidates:

            candidate["enterprise_score"] = self.calculate_score(
                candidate
            )

        candidates.sort(

            key=lambda x: (

                x["enterprise_score"],

                x["confidence"]

            ),

            reverse=True

        )

        return candidates[0]

    # -----------------------------------------------------
    # Enterprise Score
    # -----------------------------------------------------

    def calculate_score(self, candidate):

        score = candidate["confidence"]

        method = candidate["method"]

        # ---------------------------------------------
        # Exact Match
        # ---------------------------------------------

        if method == "Exact":
            score += 50

        # ---------------------------------------------
        # Normalized
        # ---------------------------------------------

        elif method == "Normalized":
            score += 40

        # ---------------------------------------------
        # D365 Dictionary
        # ---------------------------------------------

        elif method == "D365 Dictionary":
            score += 38

        # ---------------------------------------------
        # Business Fingerprint
        # ---------------------------------------------

        elif method == "Business Fingerprint":
            score += 35

        
        # ---------------------------------------------
        # Semantic
        # ---------------------------------------------

        elif method == "Semantic":
            score += 34

        # ---------------------------------------------
        # Business Dictionary
        # ---------------------------------------------

        elif method == "Business Dictionary":
            score += 32

        # ---------------------------------------------
        # Business Token
        # ---------------------------------------------

        elif method == "Business Token":
            score += 30

        # ---------------------------------------------
        # Contains
        # ---------------------------------------------

        elif method == "Contains":
            score += 20

        # ---------------------------------------------
        # Token
        # ---------------------------------------------

        elif method == "Token":
            score += 15

        # ---------------------------------------------
        # Description
        # ---------------------------------------------

        elif method == "Description":
            score += 10

        # ---------------------------------------------
        # Source Description
        # ---------------------------------------------

        elif method == "Source Description":
            score += 8

        # ---------------------------------------------
        # Acronym
        # ---------------------------------------------

        elif method == "Abbreviation":
            score += 5

        # ---------------------------------------------
        # Fuzzy
        # ---------------------------------------------

        elif method == "Fuzzy":
            score += 2

        return score