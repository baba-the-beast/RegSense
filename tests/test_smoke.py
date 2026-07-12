import sqlite3
from datetime import date
from pathlib import Path

from regsense.config import load_config
from regsense.persistence.db import SCHEMA
from regsense.persistence.repository import Repository
from regsense.pipeline import run_pipeline
from regsense.services.tracking_service import check_escalations, close_item

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def make_repo():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return Repository(conn)


def test_pipeline_produces_circulars_gaps_and_checklist():
    config = load_config(CONFIG_PATH)
    repo = make_repo()
    run_pipeline(config, repo, today=date(2026, 7, 1))

    circulars = repo.list_circulars()
    gaps = repo.list_gaps()
    items = repo.list_checklist_items()

    assert len(circulars) == 4
    assert len(gaps) > 0
    # every checklist item should trace back to a non-covered gap
    gap_by_id = {g.id: g for g in gaps}
    for item in items:
        assert gap_by_id[item.gap_id].status.value in ("missing", "partial")


def test_pipeline_is_idempotent_on_checklist_status():
    """Re-running the pipeline shouldn't reset a manually closed item back
    to open."""
    config = load_config(CONFIG_PATH)
    repo = make_repo()
    run_pipeline(config, repo, today=date(2026, 7, 1))

    items = repo.list_checklist_items()
    assert items, "expected at least one checklist item for this to be a meaningful test"
    first_id = items[0].id
    repo.update_item_status(first_id, close_item(items[0]).status)

    run_pipeline(config, repo, today=date(2026, 7, 1))
    items_after = repo.list_checklist_items()
    reloaded = next(i for i in items_after if i.id == first_id)
    assert reloaded.status.value == "closed"


def test_escalation_flags_overdue_open_items():
    config = load_config(CONFIG_PATH)
    repo = make_repo()
    run_pipeline(config, repo, today=date(2026, 6, 1))

    items = repo.list_checklist_items()
    far_future = date(2026, 12, 1)
    escalated = check_escalations(items, config, today=far_future)
    assert any(i.status.value == "escalated" for i in escalated)
