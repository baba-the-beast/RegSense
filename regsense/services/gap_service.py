"""Gap analysis: compare each circular obligation against the intermediary's
internal policy corpus and classify how well it's already covered.

Today this is a transparent token-overlap heuristic (Jaccard similarity),
not a real embedding search. It's fully inspectable and testable, and it
sits behind the GapAnalyzer interface so an EmbeddingGapAnalyzer (real RAG
over a vector store) can be swapped in later without touching the pipeline
or UI — see EmbeddingGapAnalyzer below and README's honesty table.
"""
from __future__ import annotations

import re
from typing import Protocol

from regsense.config import Config
from regsense.domain.models import Circular, Gap, GapStatus, PolicyClause

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "of", "to", "for", "and", "or", "shall",
    "must", "in", "on", "by", "with", "any", "every", "this", "that", "be",
}


def tokenize(text: str) -> set[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    return {t for t in tokens if t not in _STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


class GapAnalyzer(Protocol):
    """Interface a real gap-detection engine (RAG over a vector store,
    fine-tuned classifier) would implement to replace HeuristicGapAnalyzer."""

    def analyze(
        self, circular: Circular, clauses: tuple[PolicyClause, ...]
    ) -> tuple[Gap, ...]: ...


class HeuristicGapAnalyzer:
    def __init__(self, config: Config) -> None:
        self.config = config

    def analyze(
        self, circular: Circular, clauses: tuple[PolicyClause, ...]
    ) -> tuple[Gap, ...]:
        gaps = []
        for idx, obligation in enumerate(circular.obligations):
            obligation_tokens = tokenize(obligation)
            best_clause: PolicyClause | None = None
            best_score = 0.0
            for clause in clauses:
                score = jaccard(obligation_tokens, tokenize(clause.text))
                if score > best_score:
                    best_score = score
                    best_clause = clause

            status = self._classify(best_score)
            rationale = (
                f"Best match: '{best_clause.source_doc}' (score {best_score:.2f})"
                if best_clause
                else "No matching internal policy clause found."
            )
            gaps.append(
                Gap(
                    id=f"{circular.id}::{idx}",
                    circular_id=circular.id,
                    obligation=obligation,
                    status=status,
                    score=round(best_score, 4),
                    matched_clause_id=best_clause.id if best_clause else None,
                    rationale=rationale,
                )
            )
        return tuple(gaps)

    def _classify(self, score: float) -> GapStatus:
        t = self.config.gap_thresholds
        if score >= t.covered_min:
            return GapStatus.COVERED
        if score >= t.partial_min:
            return GapStatus.PARTIAL
        return GapStatus.MISSING


class EmbeddingGapAnalyzer:
    """Stub documenting the production path: embed obligations and policy
    clauses with a domain-tuned model, retrieve top-k via a vector store,
    and score with cosine similarity instead of token overlap. Not
    implemented in this build — see README's honesty table."""

    def analyze(
        self, circular: Circular, clauses: tuple[PolicyClause, ...]
    ) -> tuple[Gap, ...]:
        raise NotImplementedError(
            "EmbeddingGapAnalyzer requires a vector store and an embedding "
            "model; not wired up in this prototype."
        )


SYNTHETIC_POLICY_CLAUSES: tuple[PolicyClause, ...] = (
    PolicyClause(
        id="POL-001",
        source_doc="Algo Trading SOP v3",
        text=(
            "The firm discloses algorithm approval status to clients during "
            "onboarding via the standard client agreement."
        ),
    ),
    PolicyClause(
        id="POL-002",
        source_doc="KYC Handbook v5",
        text=(
            "New account KYC is completed within five working days using "
            "physical document verification at the branch."
        ),
    ),
    PolicyClause(
        id="POL-003",
        source_doc="Surveillance Policy v2",
        text=(
            "Suspicious trade alerts are reviewed weekly by the compliance "
            "desk and escalated at their discretion."
        ),
    ),
    PolicyClause(
        id="POL-004",
        source_doc="RPT Reporting Guideline v1",
        text=(
            "Related-party transaction disclosures are filed quarterly in "
            "the standard board-report format."
        ),
    ),
)
