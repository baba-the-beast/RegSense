from pathlib import Path

from regsense.config import load_config
from regsense.domain.models import Circular, GapStatus, PolicyClause
from regsense.services.gap_service import HeuristicGapAnalyzer, jaccard, tokenize

CONFIG = load_config(Path(__file__).resolve().parent.parent / "config.yaml")


def test_tokenize_strips_stopwords_and_punctuation():
    tokens = tokenize("The firm shall report this to the exchange.")
    assert "the" not in tokens
    assert "shall" not in tokens
    assert "report" in tokens
    assert "exchange" in tokens


def test_jaccard_identical_sets_is_one():
    a = {"report", "exchange"}
    assert jaccard(a, a) == 1.0


def test_jaccard_disjoint_sets_is_zero():
    assert jaccard({"report"}, {"kyc"}) == 0.0


def test_jaccard_empty_set_is_zero():
    assert jaccard(set(), {"report"}) == 0.0


def test_analyze_classifies_covered_when_score_high():
    circular = Circular(
        id="C1", title="t", category="disclosure", issued_date="2026-01-01",
        obligations=("Intermediaries shall report suspicious trades to the exchange.",),
    )
    clauses = (
        PolicyClause(id="P1", source_doc="doc", text="Suspicious trades are reported to the exchange."),
    )
    analyzer = HeuristicGapAnalyzer(CONFIG)
    gaps = analyzer.analyze(circular, clauses)
    assert len(gaps) == 1
    assert gaps[0].status == GapStatus.COVERED
    assert gaps[0].matched_clause_id == "P1"


def test_analyze_classifies_missing_when_no_relevant_clause():
    circular = Circular(
        id="C2", title="t", category="disclosure", issued_date="2026-01-01",
        obligations=("Firms must publish quarterly beneficial ownership disclosures.",),
    )
    clauses = (
        PolicyClause(id="P2", source_doc="doc", text="Employee leave requests are approved by HR."),
    )
    analyzer = HeuristicGapAnalyzer(CONFIG)
    gaps = analyzer.analyze(circular, clauses)
    assert gaps[0].status == GapStatus.MISSING


def test_analyze_handles_no_clauses():
    circular = Circular(
        id="C3", title="t", category="disclosure", issued_date="2026-01-01",
        obligations=("Firms shall report immediately.",),
    )
    analyzer = HeuristicGapAnalyzer(CONFIG)
    gaps = analyzer.analyze(circular, ())
    assert gaps[0].status == GapStatus.MISSING
    assert gaps[0].matched_clause_id is None
