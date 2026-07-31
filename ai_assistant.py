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
            "temperature": 0,
            "max_tokens": 600,
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
        except error.URLError:
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
            "temperature": 0,
            "max_tokens": 600,
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
        fuzzy_threshold=55
    ):
        """
        For purely generic source fields, bypass the Python scorer entirely.
        Use direct fuzzy matching against all targets.
        This allows [Name] → OrganizationName, PersonName, etc. to be suggested.
        """
        suggestions = []

        for target in target_metadata:
            target_field = target.get("field", "")
            target_description = target.get("description", "")

            if target_field == "" or target_field in excluded_targets:
                continue

            if violates_business_rule(source_field, target_field):
                continue

            # Direct fuzzy match without Python scorer
            fuzzy_score = fuzz.partial_ratio(
                source_field.lower(),
                target_field.lower()
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
        
        For PURELY GENERIC fields (e.g., [Name], [No_], [Phone No_]):
        - Bypass the Python scorer entirely
        - Use direct fuzzy matching at 55% threshold
        - Return highest fuzzy matches
        
        For all other fields:
        - Use Python scorer with 60% confidence threshold
        """

        if not source or not target_metadata:
            return []

        excluded = set(exclude_targets or [])

        source_field = source.get("field", "")
        source_description = source.get("description", "")

        if source_field == "":
            return []

        is_generic = self._is_purely_generic(source_field)

        # For purely generic fields, skip Python scorer and use direct fuzzy matching
        if is_generic:
            candidates = self._suggest_generic_fuzzy(
                source_field,
                source_description,
                target_metadata,
                excluded,
                fuzzy_threshold=60
            )
            
            output = []
            for c in candidates[:self.top_n]:
                output.append({
                    "target_field": c["target_field"],
                    "target_description": c["target_description"],
                    "confidence": c["confidence"],
                    "method": c["method"],
                    "reason": c["reason"],
                })

            if llm_reranker and output:
                reranked = llm_reranker.rerank_targets(source, output)
                if reranked:
                    return reranked

            return output

        # ===== For NON-GENERIC fields, use Python scorer (original logic) =====
        # Threshold of 80 filters out weak semantic cross-domain matches
        # (e.g. [Last Statement No.] → PersonLastNamePrefix via 'last' token overlap)
        min_confidence_threshold = 80

        strict_candidates = []
        fallback_candidates = []

        for target in target_metadata:

            target_field = target.get("field", "")
            target_description = target.get("description", "")

            if target_field == "":
                continue

            if target_field in excluded:
                continue

            if violates_business_rule(source_field, target_field):
                continue

            result = self.scorer.score(
                source_field=source_field,
                source_description=source_description,
                target_field=target_field,
                target_description=target_description,
            )

            if result["confidence"] < min_confidence_threshold:
                continue

            overlap_count, target_token_count = self._overlap_metrics(
                source_field,
                target_field,
            )

            method = result["method"]

            if method in HEURISTIC_METHODS:

                if result["confidence"] < HEURISTIC_MIN_CONFIDENCE:
                    fallback_candidates.append({
                        "target_field": target_field,
                        "target_description": target_description,
                        "confidence": result["confidence"],
                        "method": method,
                        "reason": result["reason"],
                        "overlap_count": overlap_count,
                        "deterministic": False,
                    })
                    continue

                if method in STRICT_OVERLAP_METHODS and overlap_count == 0:
                    continue

                if (
                    method == "Fuzzy"
                    and target_token_count > 1
                    and overlap_count < 2
                ):
                    fallback_candidates.append({
                        "target_field": target_field,
                        "target_description": target_description,
                        "confidence": result["confidence"],
                        "method": method,
                        "reason": result["reason"],
                        "overlap_count": overlap_count,
                        "deterministic": False,
                    })
                    continue

                if method == "Abbreviation" and overlap_count == 0:
                    continue

            strict_candidates.append({
                "target_field": target_field,
                "target_description": target_description,
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
                "target_field": c["target_field"],
                "target_description": c["target_description"],
                "confidence": c["confidence"],
                "method": c["method"],
                "reason": c["reason"],
            })

        if llm_reranker and output:
            reranked = llm_reranker.rerank_targets(source, output)
            if reranked:
                return reranked

        return output
