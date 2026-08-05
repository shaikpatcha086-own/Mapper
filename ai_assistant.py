"""
===========================================================
NoMap AI Assistant
D365 Metadata Mapper V3
===========================================================

Provides suggestion candidates for rows that ended as NoMap
in the main mapping pass.
"""

import json
import os
import re
from urllib import error, request

from rapidfuzz import fuzz

from scorer import Scorer
from rules import violates_business_rule
from normalizer import tokenize
from business_dictionary import expand_tokens
from semantic_matcher import SemanticMatcher
from concept_engine import get_concepts
from d365_dictionary import get_business_concept
from config import (
    HEURISTIC_MIN_CONFIDENCE,
    DETERMINISTIC_METHODS,
    HEURISTIC_METHODS,
    STRICT_OVERLAP_METHODS,
    HEURISTIC_GATE_TOKENS,
)


class LLMTargetReranker:
    """
    Optional LLM reranker for leftover source fields.

    Uses Azure OpenAI when configured, or OpenAI-compatible endpoint.
    If not configured or request fails, callers should fall back
    to rule-based suggestions.
    """

    def __init__(self, top_n=3):

        self.top_n = top_n

        self.provider = os.getenv("LLM_PROVIDER", "azure").strip().lower()

        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
        self.azure_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21").strip()

        self.openai_endpoint = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").strip().rstrip("/")
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

    def is_configured(self):

        if self.provider == "azure":
            return all([self.azure_endpoint, self.azure_key, self.azure_deployment])

        return bool(self.openai_key)

    def rerank_targets(self, source, candidates):

        if not self.is_configured() or not candidates:
            return None

        try:
            prompt = self._build_prompt(source, candidates)
            raw = self._invoke_llm(prompt)
            parsed = self._parse_json(raw)
            if not parsed:
                return None

            ranked = []
            candidate_index = {x.get("target_field", ""): x for x in candidates}

            for item in parsed.get("recommendations", [])[:self.top_n]:
                target_field = str(item.get("target_field", "")).strip()
                if target_field == "" or target_field not in candidate_index:
                    continue

                base = candidate_index[target_field]
                confidence = item.get("confidence", base.get("confidence", 0))

                try:
                    confidence = int(confidence)
                except Exception:
                    confidence = base.get("confidence", 0)

                reason = str(item.get("reason", "")).strip() or "LLM rerank suggestion"

                ranked.append({
                    "target_field": target_field,
                    "target_description": base.get("target_description", ""),
                    "confidence": max(0, min(100, confidence)),
                    "method": "LLM Rerank",
                    "reason": reason,
                })

            return ranked or None

        except Exception:
            return None

    def _build_prompt(self, source, candidates):

        source_field = source.get("field", "")
        source_description = source.get("description", "")
        source_context = (
            source.get("source_entity", "")
            or source.get("source_sheet", "")
            or source.get("source_file", "")
        )

        trimmed_candidates = [
            {
                "target_field": x.get("target_field", ""),
                "target_description": x.get("target_description", ""),
                "rule_confidence": x.get("confidence", 0),
                "rule_method": x.get("method", ""),
                "rule_reason": x.get("reason", ""),
            }
            for x in candidates[:15]
        ]

        payload = {
            "source": {
                "field": source_field,
                "description": source_description,
                "context": source_context,
            },
            "candidate_targets": trimmed_candidates,
            "instructions": {
                "goal": "Pick best target field matches for leftover source field.",
                "constraints": [
                    "Return max 3 recommendations.",
                    "Do not invent new target fields.",
                    "Prefer business meaning over token similarity.",
                    "Return confidence 0-100 and concise reason.",
                ],
            },
            "output_schema": {
                "recommendations": [
                    {
                        "target_field": "string",
                        "confidence": 0,
                        "reason": "string",
                    }
                ]
            },
        }

        return json.dumps(payload, ensure_ascii=True)

    def _invoke_llm(self, prompt):

        if self.provider == "azure":
            return self._invoke_azure(prompt)

        return self._invoke_openai(prompt)

    def _invoke_azure(self, prompt):

        url = (
            f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}"
            f"/chat/completions?api-version={self.azure_api_version}"
        )

        body = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict metadata mapping assistant. Reply with valid JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "max_completion_tokens": 600,
        }

        req = request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "api-key": self.azure_key,
            },
        )

        try:
            with request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return payload["choices"][0]["message"]["content"]
        except error.HTTPError as e:
            import sys
            body = e.read().decode("utf-8", errors="replace")
            print(f"[AZURE HTTP ERROR] {e.code} {e.reason}: {body[:300]}", file=sys.stderr)
            return ""
        except error.URLError as e:
            import sys
            print(f"[AZURE URL ERROR] {e.reason}", file=sys.stderr)
            return ""

    def _invoke_openai(self, prompt):

        url = f"{self.openai_endpoint}/chat/completions"

        body = {
            "model": self.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict metadata mapping assistant. Reply with valid JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "max_completion_tokens": 600,
        }

        req = request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}",
            },
        )

        try:
            with request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return payload["choices"][0]["message"]["content"]
        except error.URLError:
            return ""

    def _parse_json(self, raw):

        if not raw:
            return None

        text = raw.strip()

        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None

        try:
            return json.loads(match.group(0))
        except Exception:
            return None

    def suggest_independently(self, source, target_metadata, exclude_targets=None):
        """
        LLM independently suggests target fields for a leftover source field.
        Does NOT rely on D365 Concept Match candidates — LLM gets the full
        target list and decides based on business context alone.
        Returns top suggestions with method = "LLM Suggestion".
        """
        if not self.is_configured() or not source or not target_metadata:
            return []

        excluded = set(exclude_targets or [])
        source_field = source.get("field", "")
        source_description = source.get("description", "")
        source_context = (
            source.get("source_entity", "")
            or source.get("source_sheet", "")
            or source.get("source_file", "")
        )

        if not source_field:
            return []

        # Pass all target fields to LLM (up to 60 to stay within token limits)
        target_list = [
            {
                "target_field": t.get("field", ""),
                "target_description": t.get("description", ""),
            }
            for t in target_metadata
            if t.get("field", "") and t.get("field", "") not in excluded
        ][:60]

        payload = {
            "source": {
                "field": source_field,
                "description": source_description,
                "context": source_context,
            },
            "available_targets": target_list,
            "instructions": {
                "goal": "Suggest the best D365 FO target field matches for this source field.",
                "constraints": [
                    "Return max 3 recommendations.",
                    "Only use target fields from available_targets list.",
                    "Do not invent new target fields.",
                    "Base suggestions on D365 Finance & Operations business meaning.",
                    "Return confidence 0-100 and concise business reason.",
                    "If no good match exists, return empty recommendations list.",
                ],
            },
            "output_schema": {
                "recommendations": [
                    {
                        "target_field": "string",
                        "confidence": 0,
                        "reason": "string",
                    }
                ]
            },
        }

        try:
            raw = self._invoke_llm(json.dumps(payload, ensure_ascii=True))
            parsed = self._parse_json(raw)
            if not parsed:
                return []

            target_index = {t["target_field"]: t for t in target_list}
            results = []

            for item in parsed.get("recommendations", [])[:self.top_n]:
                target_field = str(item.get("target_field", "")).strip()
                if not target_field or target_field not in target_index:
                    continue

                confidence = item.get("confidence", 0)
                try:
                    confidence = int(confidence)
                except Exception:
                    confidence = 0

                results.append({
                    "target_field": target_field,
                    "target_description": target_index[target_field].get("target_description", ""),
                    "confidence": max(0, min(100, confidence)),
                    "method": "LLM Suggestion",
                    "reason": str(item.get("reason", "")).strip() or "LLM independent suggestion",
                })

            return results

        except Exception:
            return []


class NoMapAIAssistant:

    def __init__(self, top_n=3):

        self.top_n = top_n
        self.scorer = Scorer()

    def _overlap_metrics(self, source_field, target_field):

        source_tokens = set(expand_tokens(tokenize(source_field)))
        target_tokens = set(expand_tokens(tokenize(target_field)))

        source_tokens -= HEURISTIC_GATE_TOKENS
        target_tokens -= HEURISTIC_GATE_TOKENS

        overlap = source_tokens.intersection(target_tokens)

        return len(overlap), len(target_tokens)

    def _is_generic_leftover_source(self, source_field):
        """Check if source field contains ONLY gate tokens (couldn't match in main pass)."""
        source_tokens = set(expand_tokens(tokenize(source_field)))
        meaningful_tokens = source_tokens - HEURISTIC_GATE_TOKENS
        return len(meaningful_tokens) == 0 and len(source_tokens) > 0

    def suggest_for_nomap(
        self,
        target,
        source_metadata,
        exclude_sources=None,
    ):
        """
        Return top candidate suggestions for a target field.
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
                target_description=target_description,
            )

            if result["confidence"] < 60:
                continue

            overlap_count, target_token_count = self._overlap_metrics(
                source_field,
                target_field,
            )

            method = result["method"]
            is_generic = self._is_generic_leftover_source(source_field)

            if method in HEURISTIC_METHODS:

                if result["confidence"] < HEURISTIC_MIN_CONFIDENCE:
                    fallback_candidates.append({
                        "source_field": source_field,
                        "source_description": source_description,
                        "confidence": result["confidence"],
                        "method": method,
                        "reason": result["reason"],
                        "overlap_count": overlap_count,
                        "deterministic": False,
                    })
                    continue

                # For generic leftover sources (only gate tokens), bypass strict overlap
                # because they inherently can't have meaningful token overlap
                if not is_generic and method in STRICT_OVERLAP_METHODS and overlap_count == 0:
                    continue

                if (
                    not is_generic
                    and method == "Fuzzy"
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
                        "deterministic": False,
                    })
                    continue

                if not is_generic and method == "Abbreviation" and overlap_count == 0:
                    continue

            strict_candidates.append({
                "source_field": source_field,
                "source_description": source_description,
                "confidence": result["confidence"],
                "method": method,
                "reason": result["reason"],
                "overlap_count": overlap_count,
                "deterministic": method in DETERMINISTIC_METHODS,
            })

        strict_candidates.sort(
            key=lambda x: (
                x["deterministic"],
                x["confidence"],
                x["overlap_count"],
            ),
            reverse=True,
        )

        fallback_candidates.sort(
            key=lambda x: (
                x["confidence"],
                x["overlap_count"],
            ),
            reverse=True,
        )

        candidates = strict_candidates or fallback_candidates

        output = []

        for c in candidates[:self.top_n]:
            output.append({
                "source_field": c["source_field"],
                "source_description": c["source_description"],
                "confidence": c["confidence"],
                "method": c["method"],
                "reason": c["reason"],
            })

        return output

    def _is_purely_generic(self, field):
        """
        Check if a field consists only of gate tokens (generic terms like 'name', 'id', 'no', etc.).
        These fields need special handling because they have no meaningful semantic content.
        """
        tokens = set(tokenize(field)) - {""}
        if not tokens:
            return True
        return tokens.issubset(HEURISTIC_GATE_TOKENS)

    def _suggest_generic_fuzzy(
        self,
        source_field,
        source_description,
        target_metadata,
        excluded_targets,
        fuzzy_threshold=60
    ):
        """
        For purely generic source fields, bypass the Python scorer entirely.
        Uses token_set_ratio (not partial_ratio) to avoid false substring matches.
        e.g. partial_ratio("id", "PersonMiddleName") = 100 because "id" is inside "miDdlename"
             token_set_ratio("id", "PersonMiddleName") = ~20 (correct — no real overlap)
        """
        from normalizer import normalize

        suggestions = []

        source_normalized = normalize(source_field)

        for target in target_metadata:
            target_field = target.get("field", "")
            target_description = target.get("description", "")

            if target_field == "" or target_field in excluded_targets:
                continue

            if violates_business_rule(source_field, target_field):
                continue

            target_normalized = normalize(target_field)

            # token_set_ratio compares token sets — immune to substring false positives
            fuzzy_score = fuzz.token_set_ratio(
                source_normalized,
                target_normalized
            )

            if fuzzy_score >= fuzzy_threshold:
                suggestions.append({
                    "target_field": target_field,
                    "target_description": target_description,
                    "confidence": fuzzy_score,
                    "method": "Fuzzy (Direct)",
                    "reason": "Direct fuzzy match for generic source field",
                    "overlap_count": 0,
                    "deterministic": False,
                })

        suggestions.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        return suggestions

    def suggest_targets_for_unmapped_source(
        self,
        source,
        target_metadata,
        exclude_targets=None,
        llm_reranker=None,
    ):
        """
        Return top target suggestions for a source field that remained unused.

        Strategy (NO fuzzy matching — fuzzy already ran in main pass):
        1. Expand source to D365 business concepts via ConceptEngine
        2. Score all target fields by concept overlap (SemanticMatcher)
        3. If LLM is configured, rerank the top candidates
        """

        if not source or not target_metadata:
            return []

        excluded = set(exclude_targets or [])

        source_field = source.get("field", "")
        source_description = source.get("description", "")

        if source_field == "":
            return []

        # -------------------------------------------------------
        # Step 1: Expand source to D365 business concepts
        # Strip HEURISTIC_GATE_TOKENS so generic tokens like
        # "number", "no", "state" don't drive false 100% matches
        # -------------------------------------------------------
        _GATE = HEURISTIC_GATE_TOKENS | {
            "no", "num", "nbr", "number", "id", "code", "key",
            "province", "region", "state", "value", "data",
            "record", "field", "type", "name", "group"
        }

        raw_source_concepts = set(get_concepts(source_field) or [])
        if source_description:
            raw_source_concepts.update(get_concepts(source_description) or [])
        d365_concept = get_business_concept(source_field)
        if d365_concept:
            raw_source_concepts.update(tokenize(d365_concept))

        # Meaningful concepts = strip gate tokens
        source_meaningful = raw_source_concepts - _GATE

        semantic = SemanticMatcher()

        # -------------------------------------------------------
        # Step 2: Score all targets by MEANINGFUL concept overlap
        # Require at least 1 non-generic concept to match
        # -------------------------------------------------------
        candidates = []

        for target in target_metadata:

            target_field = target.get("field", "")
            target_description = target.get("description", "")

            if target_field == "" or target_field in excluded:
                continue

            if violates_business_rule(source_field, target_field):
                continue

            raw_target_concepts = set(get_concepts(target_field) or [])
            target_meaningful = raw_target_concepts - _GATE

            # Must share at least 1 meaningful concept — no gate-only matches
            meaningful_overlap = source_meaningful.intersection(target_meaningful)
            if not meaningful_overlap:
                continue

            # Score only on meaningful concepts (avoids false 100%)
            concept_score = round(
                len(meaningful_overlap) / max(len(source_meaningful), len(target_meaningful), 1) * 100
            )

            if concept_score < 25:
                continue

            # Description bonus
            desc_bonus = 0
            if target_description and source_meaningful:
                target_desc_concepts = set(get_concepts(target_description) or []) - _GATE
                desc_overlap = source_meaningful.intersection(target_desc_concepts)
                if desc_overlap:
                    desc_bonus = min(len(desc_overlap) * 5, 20)

            final_score = min(100, concept_score + desc_bonus)

            matching = sorted(meaningful_overlap)
            reason = (
                f"D365 concept match: {', '.join(matching)}"
                if matching
                else "D365 semantic concept similarity"
            )

            candidates.append({
                "target_field": target_field,
                "target_description": target_description,
                "confidence": final_score,
                "method": "D365 Concept Match",
                "reason": reason,
            })

        # -------------------------------------------------------
        # Step 3: Sort by confidence, take top N (threshold >= 50)
        # -------------------------------------------------------
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        d365_output = [c for c in candidates[:self.top_n] if c["confidence"] >= 50]

        # -------------------------------------------------------
        # Step 4: LLM independent suggestion (if configured)
        # Run regardless of whether D365 found candidates
        # -------------------------------------------------------
        llm_output = []
        if llm_reranker:
            try:
                llm_output = llm_reranker.suggest_independently(
                    source, target_metadata, exclude_targets=excluded
                )
                import sys
                print(f"[LLM DEBUG] source={source.get('field','')} llm_raw={llm_output}", file=sys.stderr)
            except Exception as llm_err:
                import sys
                print(f"[LLM ERROR] source={source.get('field','')} error={llm_err}", file=sys.stderr)
                llm_output = []
            # Filter LLM results to >= 50 confidence
            llm_output = [c for c in llm_output if c.get("confidence", 0) >= 50]

        # -------------------------------------------------------
        # Step 5: Pick winner — highest confidence >= 50
        # If both have results, compare top scores and pick best
        # -------------------------------------------------------
        if d365_output and llm_output:
            d365_top = d365_output[0]["confidence"]
            llm_top = llm_output[0]["confidence"]
            return llm_output if llm_top >= d365_top else d365_output

        if llm_output:
            return llm_output

        if d365_output:
            return d365_output

        return []

