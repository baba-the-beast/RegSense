"""Config-driven parameters for RegSense.

Every threshold, offset, and owner name a reviewer would expect to find
hardcoded lives in config.yaml instead. This module loads it, validates it,
and hands back a typed Config object so the rest of the codebase never
touches raw dicts.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


class ConfigError(ValueError):
    """Raised when config.yaml is missing required keys or has values
    outside sane bounds."""


@dataclass(frozen=True)
class GapThresholds:
    covered_min: float
    partial_min: float


@dataclass(frozen=True)
class SeverityConfig:
    high_keywords: tuple[str, ...]
    medium_keywords: tuple[str, ...]


@dataclass(frozen=True)
class Config:
    max_circulars: int
    gap_thresholds: GapThresholds
    severity: SeverityConfig
    due_date_offsets_days: dict[str, int]
    escalation_overdue_days: int
    owners: tuple[str, ...]
    raw: dict[str, Any] = field(repr=False, compare=False)


def _require(d: dict, key: str, path: str) -> Any:
    if key not in d:
        raise ConfigError(f"Missing required config key: {path}.{key}")
    return d[key]


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> Config:
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    corpus_raw = _require(raw, "corpus", "")
    max_circulars = _require(corpus_raw, "max_circulars", "corpus")

    gap_raw = _require(raw, "gap_thresholds", "")
    thresholds = GapThresholds(
        covered_min=_require(gap_raw, "covered_min", "gap_thresholds"),
        partial_min=_require(gap_raw, "partial_min", "gap_thresholds"),
    )
    if not (0 <= thresholds.partial_min <= thresholds.covered_min <= 1):
        raise ConfigError(
            "gap_thresholds must satisfy 0 <= partial_min <= covered_min <= 1"
        )

    sev_raw = _require(raw, "severity_keywords", "")
    severity = SeverityConfig(
        high_keywords=tuple(_require(sev_raw, "high", "severity_keywords")),
        medium_keywords=tuple(_require(sev_raw, "medium", "severity_keywords")),
    )

    offsets_raw = _require(raw, "due_date_offsets_days", "")
    offsets = {
        "high": _require(offsets_raw, "high", "due_date_offsets_days"),
        "medium": _require(offsets_raw, "medium", "due_date_offsets_days"),
        "low": _require(offsets_raw, "low", "due_date_offsets_days"),
    }
    for level, days in offsets.items():
        if days <= 0:
            raise ConfigError(f"due_date_offsets_days.{level} must be positive, got {days}")

    escalation_days = _require(raw, "escalation_overdue_days", "")
    if escalation_days <= 0:
        raise ConfigError("escalation_overdue_days must be positive")

    owners = tuple(_require(raw, "owners", ""))
    if not owners:
        raise ConfigError("owners must have at least one entry")

    return Config(
        max_circulars=max_circulars,
        gap_thresholds=thresholds,
        severity=severity,
        due_date_offsets_days=offsets,
        escalation_overdue_days=escalation_days,
        owners=owners,
        raw=copy.deepcopy(raw),
    )
