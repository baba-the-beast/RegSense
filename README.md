# RegSense

Agentic compliance copilot for SEBI intermediaries — ingestion agent pulls
obligations out of a circular → gap agent compares each obligation against
the internal policy corpus → checklist agent turns every uncovered
obligation into an owned, dated task → tracking agent auto-escalates
anything left open past its due date. Built as a SEBI-flavoured demo on
synthetic circulars and a synthetic policy corpus.

## Run it

```
pip install -r requirements.txt
streamlit run app.py
```

## Run the tests

```
pip install -r requirements.txt
pytest tests/ -v
```

## Project layout

`app.py` is UI orchestration only. `regsense/services/` holds ingestion,
gap analysis, checklist generation, and tracking as independently testable
modules, each behind a swappable interface. `regsense/persistence/` is the
SQLite-backed state layer. `config.yaml` holds every threshold, owner name,
and due-date offset — nothing tunable is hardcoded in the modules.

## What's real vs faked here

| Part | This build | Actual system |
|---|---|---|
| Circular corpus | 4 synthetic, hand-written circulars | Live SEBI circular feed / document upload pipeline |
| Obligation extraction | Keyword-marker sentence filter (`shall`, `must`, ...) | NER model trained on regulatory language |
| Policy corpus | 4 synthetic internal policy clauses | Real SOP/policy document store, chunked and indexed |
| Gap scoring | Jaccard token-overlap heuristic | Embedding search (`EmbeddingGapAnalyzer`, stubbed today) over a vector store |
| Severity & owner assignment | Keyword rules + deterministic round-robin | Escalation policy engine wired to the firm's actual org chart |
| Escalation | Overdue-days check on page load | Scheduled job + notification (email/Slack) integration |
| Persistence | Local SQLite file | Postgres with multi-user isolation and audit-grade retention |

Both the gap-scoring and obligation-extraction steps sit behind explicit
interfaces (`GapAnalyzer`, and `CircularSource` for ingestion) — swapping
in a real embedding search or a live circular feed is a wiring change in
`pipeline.py`, not a rewrite of the services or UI around them.

## Security & compliance notes (synthetic data, but worth stating plainly)

- No secrets are used or required by this build; there's nothing to leak.
- This handles **no real regulatory or customer data** — the circulars and
  policy clauses are synthetic and clearly fictional. A production version
  ingesting real SEBI circulars and real internal policy documents would
  need, at minimum: access controls scoped to compliance staff, an
  immutable audit log of every gap classification and checklist action,
  and a documented review process before any auto-generated task is acted
  on. None of that exists here — every classification in this build is a
  heuristic, stated as such throughout (see table above).
"# RegSense" 
