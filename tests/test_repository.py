import sqlite3

import pytest

from regsense.domain.models import (
    ChecklistItem,
    Circular,
    Gap,
    GapStatus,
    Severity,
    TaskStatus,
)
from regsense.persistence.db import SCHEMA
from regsense.persistence.repository import Repository


@pytest.fixture
def repo():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return Repository(conn)


def test_save_and_list_circulars(repo):
    c = Circular(id="C1", title="Title", category="disclosure", issued_date="2026-06-01")
    repo.save_circulars((c,))
    result = repo.list_circulars()
    assert len(result) == 1
    assert result[0].id == "C1"
    assert result[0].title == "Title"


def test_save_circulars_upserts_on_id(repo):
    c1 = Circular(id="C1", title="Old", category="disclosure", issued_date="2026-06-01")
    c2 = Circular(id="C1", title="New", category="disclosure", issued_date="2026-06-01")
    repo.save_circulars((c1,))
    repo.save_circulars((c2,))
    result = repo.list_circulars()
    assert len(result) == 1
    assert result[0].title == "New"


def test_save_and_list_gaps(repo):
    repo.save_circulars((Circular(id="C1", title="t", category="d", issued_date="2026-06-01"),))
    g = Gap(id="g1", circular_id="C1", obligation="x", status=GapStatus.MISSING,
            score=0.1, matched_clause_id=None, rationale="none")
    repo.save_gaps((g,))
    result = repo.list_gaps(circular_id="C1")
    assert len(result) == 1
    assert result[0].status == GapStatus.MISSING


def test_save_and_list_checklist_items(repo):
    repo.save_circulars((Circular(id="C1", title="t", category="d", issued_date="2026-06-01"),))
    repo.save_gaps((Gap(id="g1", circular_id="C1", obligation="x", status=GapStatus.MISSING,
                         score=0.1, matched_clause_id=None, rationale="none"),))
    item = ChecklistItem(id="t1", gap_id="g1", description="Close it", owner="Ops Lead",
                          severity=Severity.HIGH, due_date="2026-07-05", status=TaskStatus.OPEN)
    repo.save_checklist_items((item,))
    result = repo.list_checklist_items()
    assert len(result) == 1
    assert result[0].status == TaskStatus.OPEN


def test_update_item_status(repo):
    repo.save_circulars((Circular(id="C1", title="t", category="d", issued_date="2026-06-01"),))
    repo.save_gaps((Gap(id="g1", circular_id="C1", obligation="x", status=GapStatus.MISSING,
                         score=0.1, matched_clause_id=None, rationale="none"),))
    item = ChecklistItem(id="t1", gap_id="g1", description="Close it", owner="Ops Lead",
                          severity=Severity.HIGH, due_date="2026-07-05", status=TaskStatus.OPEN)
    repo.save_checklist_items((item,))
    repo.update_item_status("t1", TaskStatus.CLOSED)
    result = repo.list_checklist_items()
    assert result[0].status == TaskStatus.CLOSED
