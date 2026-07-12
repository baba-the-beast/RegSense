from __future__ import annotations

import streamlit as st

from regsense.persistence.repository import Repository


def render_circulars(repo: Repository) -> None:
    st.subheader("Ingested circulars")
    circulars = repo.list_circulars()
    if not circulars:
        st.info("No circulars yet — run the pipeline from the sidebar.")
        return

    gaps = repo.list_gaps()
    for c in circulars:
        c_gaps = [g for g in gaps if g.circular_id == c.id]
        with st.container(border=True):
            st.markdown(f"**{c.title}**")
            st.caption(f"{c.id} · {c.category} · issued {c.issued_date}")
            st.write(f"{len(c_gaps)} obligation(s) extracted")
