"""Turns MISSING/PARTIAL gaps into an owned, dated compliance checklist.

Severity and owner assignment are both rule-based and fully config-driven
(see config.yaml: severity_keywords, owners, due_date_offsets_days) — no
model in the loop yet. That keeps every assignment traceable back to a
rule a reviewer can read, which matters more here than in scoring: a
checklist a compliance team can't audit is worse than no checklist.
"""
from __future__ import annotations

from datetime import date, timedelta

from regsense.config import Config
from regsense.domain.models import ChecklistItem, Gap, GapStatus, Severity, TaskStatus


def classify_severity(obligation_text: str, config: Config) -> Severity:
    text = obligation_text.lower()
    if any(kw in text for kw in config.severity.high_keywords):
        return Severity.HIGH
    if any(kw in text for kw in config.severity.medium_keywords):
        return Severity.MEDIUM
    return Severity.LOW


def assign_owner(gap_id: str, config: Config) -> str:
    """Deterministic round-robin over config.owners, keyed on the gap id so
    the same gap always gets the same owner across re-runs."""
    idx = sum(ord(c) for c in gap_id) % len(config.owners)
    return config.owners[idx]


def compute_due_date(severity: Severity, config: Config, today: date) -> str:
    offset_days = config.due_date_offsets_days[severity.value]
    return (today + timedelta(days=offset_days)).isoformat()


class ChecklistGenerator:
    def __init__(self, config: Config) -> None:
        self.config = config

    def generate(
        self, gaps: tuple[Gap, ...], today: date | None = None
    ) -> tuple[ChecklistItem, ...]:
        today = today or date.today()
        items = []
        for gap in gaps:
            if gap.status == GapStatus.COVERED:
                continue
            severity = classify_severity(gap.obligation, self.config)
            owner = assign_owner(gap.id, self.config)
            due_date = compute_due_date(severity, self.config, today)
            verb = "Close" if gap.status == GapStatus.MISSING else "Strengthen"
            description = f"{verb} coverage for: {gap.obligation}"
            items.append(
                ChecklistItem(
                    id=f"task::{gap.id}",
                    gap_id=gap.id,
                    description=description,
                    owner=owner,
                    severity=severity,
                    due_date=due_date,
                    status=TaskStatus.OPEN,
                )
            )
        return tuple(items)
