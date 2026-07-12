"""Tracks checklist item lifecycle: closing, and auto-escalating anything
open past its due date by more than the configured grace period.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date

from regsense.config import Config
from regsense.domain.models import ChecklistItem, TaskStatus


def close_item(item: ChecklistItem) -> ChecklistItem:
    return replace(item, status=TaskStatus.CLOSED)


def check_escalations(
    items: tuple[ChecklistItem, ...], config: Config, today: date | None = None
) -> tuple[ChecklistItem, ...]:
    """Returns a new tuple with any OPEN item overdue by more than
    config.escalation_overdue_days flipped to ESCALATED. Already-closed or
    already-escalated items pass through unchanged."""
    today = today or date.today()
    updated = []
    for item in items:
        if item.status != TaskStatus.OPEN:
            updated.append(item)
            continue
        due = date.fromisoformat(item.due_date)
        overdue_days = (today - due).days
        if overdue_days > config.escalation_overdue_days:
            updated.append(replace(item, status=TaskStatus.ESCALATED))
        else:
            updated.append(item)
    return tuple(updated)
