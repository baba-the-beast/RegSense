from datetime import date
from pathlib import Path

from regsense.config import load_config
from regsense.domain.models import Gap, GapStatus, Severity, TaskStatus
from regsense.services.checklist_service import (
    ChecklistGenerator,
    assign_owner,
    classify_severity,
    compute_due_date,
)

CONFIG = load_config(Path(__file__).resolve().parent.parent / "config.yaml")


def test_classify_severity_high_on_penalty_keyword():
    assert classify_severity("Failure will attract a penalty.", CONFIG) == Severity.HIGH


def test_classify_severity_medium_on_reporting_keyword():
    assert classify_severity("Must be included in the monthly reporting.", CONFIG) == Severity.MEDIUM


def test_classify_severity_low_when_no_keyword_matches():
    assert classify_severity("The office will be repainted next month.", CONFIG) == Severity.LOW


def test_assign_owner_is_deterministic():
    assert assign_owner("gap-1", CONFIG) == assign_owner("gap-1", CONFIG)


def test_assign_owner_is_within_configured_owners():
    assert assign_owner("gap-42", CONFIG) in CONFIG.owners


def test_compute_due_date_offsets_from_today():
    from datetime import timedelta

    today = date(2026, 7, 1)
    due = compute_due_date(Severity.HIGH, CONFIG, today)
    expected = today + timedelta(days=CONFIG.due_date_offsets_days["high"])
    assert due == expected.isoformat()


def test_generator_skips_covered_gaps():
    gaps = (
        Gap(id="g1", circular_id="c1", obligation="Firms shall report suspicious trades.",
            status=GapStatus.COVERED, score=0.9, matched_clause_id="P1", rationale="matched"),
    )
    generator = ChecklistGenerator(CONFIG)
    items = generator.generate(gaps, today=date(2026, 7, 1))
    assert items == ()


def test_generator_creates_item_for_missing_gap():
    gaps = (
        Gap(id="g2", circular_id="c1", obligation="Firms shall report suspicious trades, or face a penalty.",
            status=GapStatus.MISSING, score=0.1, matched_clause_id=None, rationale="no match"),
    )
    generator = ChecklistGenerator(CONFIG)
    items = generator.generate(gaps, today=date(2026, 7, 1))
    assert len(items) == 1
    assert items[0].status == TaskStatus.OPEN
    assert items[0].severity == Severity.HIGH
    assert items[0].gap_id == "g2"
