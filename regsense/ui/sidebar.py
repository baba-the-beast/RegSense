from __future__ import annotations

import streamlit as st

from regsense.config import Config
from regsense.persistence.repository import Repository
from regsense.pipeline import run_pipeline


def render_sidebar(config: Config, repo: Repository) -> None:
    st.sidebar.title("RegSense")
    st.sidebar.caption("Agentic compliance copilot — synthetic demo data")

    if st.sidebar.button("Run ingestion + gap analysis", use_container_width=True):
        run_pipeline(config, repo)
        st.sidebar.success("Pipeline run complete.")

    circulars = repo.list_circulars()
    gaps = repo.list_gaps()
    items = repo.list_checklist_items()

    st.sidebar.markdown("---")
    st.sidebar.metric("Circulars ingested", len(circulars))
    st.sidebar.metric("Obligations analyzed", len(gaps))
    st.sidebar.metric("Open checklist tasks", sum(1 for i in items if i.status.value == "open"))

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Gap scoring is a token-overlap heuristic today, not a real "
        "embedding search — see README."
    )
