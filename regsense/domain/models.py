"""Domain models for RegSense.

Plain dataclasses with no framework dependencies (no Streamlit, no SQLite
row types leaking through) so services and tests can be written against
them directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class Circular:
    """A SEBI circular, reduced to the obligation sentences an ingestion
    step pulled out of it (see services/ingestion_service.py)."""

    id: str
    title: str
    category: str
    issued_date: str
    obligations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PolicyClause:
    """A single clause from the intermediary's internal policy/SOP corpus."""

    id: str
    source_doc: str
    text: str


class GapStatus(str, Enum):
    COVERED = "covered"
    PARTIAL = "partial"
    MISSING = "missing"


@dataclass(frozen=True)
class Gap:
    """Result of comparing one obligation sentence against the best-matching
    internal policy clause."""

    id: str
    circular_id: str
    obligation: str
    status: GapStatus
    score: float
    matched_clause_id: str | None
    rationale: str


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    ESCALATED = "escalated"


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    gap_id: str
    description: str
    owner: str
    severity: Severity
    due_date: str
    status: TaskStatus = TaskStatus.OPEN
