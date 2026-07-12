from __future__ import annotations

import pandas as pd
import streamlit as st

from regsense.persistence.repository import Repository
from regsense.ui.styles import badge


def render_gaps(repo: Repository) -> None:
    st.subheader("Gap analysis")
    gaps = repo.list_gaps()
    if not gaps:
        st.info("No gaps yet — run the pipeline from the sidebar.")
        return

    status_class = {"covered": "rs-covered", "partial": "rs-partial", "missing": "rs-missing"}
    rows = []
    for g in gaps:
        rows.append(
            {
                "Circular": g.circular_id,
                "Obligation": g.obligation,
                "Status": badge(g.status.value.upper(), status_class[g.status.value]),
                "Score": f"{g.score:.2f}",
                "Rationale": g.rationale,
            }
        )
    df = pd.DataFrame(rows)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
