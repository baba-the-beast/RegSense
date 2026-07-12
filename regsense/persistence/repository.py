"""Every query RegSense runs, in one place, so the UI and pipeline never
write raw SQL themselves.
"""
from __future__ import annotations

import sqlite3

from regsense.domain.models import (
    ChecklistItem,
    Circular,
    Gap,
    GapStatus,
    Severity,
    TaskStatus,
)


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # -- circulars --------------------------------------------------
    def save_circulars(self, circulars: tuple[Circular, ...]) -> None:
        with self.conn:
            for c in circulars:
                self.conn.execute(
                    "INSERT OR REPLACE INTO circulars (id, title, category, issued_date) "
                    "VALUES (?, ?, ?, ?)",
                    (c.id, c.title, c.category, c.issued_date),
                )

    def list_circulars(self) -> tuple[Circular, ...]:
        rows = self.conn.execute("SELECT * FROM circulars ORDER BY issued_date").fetchall()
        return tuple(
            Circular(
                id=r["id"], title=r["title"], category=r["category"],
                issued_date=r["issued_date"], obligations=(),
            )
            for r in rows
        )

    # -- gaps ---------------------------------------------------------
    def save_gaps(self, gaps: tuple[Gap, ...]) -> None:
        with self.conn:
            for g in gaps:
                self.conn.execute(
                    "INSERT OR REPLACE INTO gaps "
                    "(id, circular_id, obligation, status, score, matched_clause_id, rationale) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (g.id, g.circular_id, g.obligation, g.status.value, g.score,
                     g.matched_clause_id, g.rationale),
                )

    def list_gaps(self, circular_id: str | None = None) -> tuple[Gap, ...]:
        if circular_id:
            rows = self.conn.execute(
                "SELECT * FROM gaps WHERE circular_id = ? ORDER BY id", (circular_id,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM gaps ORDER BY id").fetchall()
        return tuple(
            Gap(
                id=r["id"], circular_id=r["circular_id"], obligation=r["obligation"],
                status=GapStatus(r["status"]), score=r["score"],
                matched_clause_id=r["matched_clause_id"], rationale=r["rationale"],
            )
            for r in rows
        )

    # -- checklist items ------------------------------------------------
    def save_checklist_items(self, items: tuple[ChecklistItem, ...]) -> None:
        with self.conn:
            for i in items:
                self.conn.execute(
                    "INSERT OR REPLACE INTO checklist_items "
                    "(id, gap_id, description, owner, severity, due_date, status) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (i.id, i.gap_id, i.description, i.owner, i.severity.value,
                     i.due_date, i.status.value),
                )

    def list_checklist_items(self) -> tuple[ChecklistItem, ...]:
        rows = self.conn.execute(
            "SELECT * FROM checklist_items ORDER BY due_date"
        ).fetchall()
        return tuple(
            ChecklistItem(
                id=r["id"], gap_id=r["gap_id"], description=r["description"],
                owner=r["owner"], severity=Severity(r["severity"]),
                due_date=r["due_date"], status=TaskStatus(r["status"]),
            )
            for r in rows
        )

    def update_item_status(self, item_id: str, status: TaskStatus) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE checklist_items SET status = ? WHERE id = ?",
                (status.value, item_id),
            )
