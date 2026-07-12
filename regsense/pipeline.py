"""Wires the four stages together: ingest circulars, analyze gaps against
the policy corpus, generate a checklist, persist everything. UI code calls
this module rather than the services directly.
"""
from __future__ import annotations

from datetime import date

from regsense.config import Config
from regsense.persistence.repository import Repository
from regsense.services.checklist_service import ChecklistGenerator
from regsense.services.gap_service import SYNTHETIC_POLICY_CLAUSES, HeuristicGapAnalyzer
from regsense.services.ingestion_service import CircularIngestionService


def run_pipeline(config: Config, repo: Repository, today: date | None = None) -> None:
    """Runs ingestion -> gap analysis -> checklist generation once and
    persists every stage's output. Idempotent: re-running overwrites
    circulars/gaps but never resets an already-CLOSED/ESCALATED checklist
    item's status, since save_checklist_items uses INSERT OR REPLACE on id
    and generate() only ever produces OPEN items for a gap id — a caller
    that wants to preserve manual status changes should call
    generate_and_persist_new_only in that scenario; see tests."""
    ingestion = CircularIngestionService()
    circulars = ingestion.ingest()
    repo.save_circulars(circulars)

    analyzer = HeuristicGapAnalyzer(config)
    all_gaps = []
    for circular in circulars:
        all_gaps.extend(analyzer.analyze(circular, SYNTHETIC_POLICY_CLAUSES))
    repo.save_gaps(tuple(all_gaps))

    existing_item_ids = {i.id for i in repo.list_checklist_items()}
    generator = ChecklistGenerator(config)
    new_items = generator.generate(tuple(all_gaps), today=today)
    items_to_save = tuple(i for i in new_items if i.id not in existing_item_ids)
    repo.save_checklist_items(items_to_save)
