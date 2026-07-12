from __future__ import annotations

from datetime import date

import streamlit as st

from regsense.config import Config
from regsense.domain.models import TaskStatus
from regsense.persistence.repository import Repository
from regsense.services.tracking_service import check_escalations, close_item


def render_checklist(config: Config, repo: Repository) -> None:
    st.subheader("Compliance checklist")

    items = repo.list_checklist_items()
    if not items:
        st.info("No checklist items yet — run the pipeline from the sidebar.")
        return

    escalated = check_escalations(items, config, today=date.today())
    for item in escalated:
        if item.status == TaskStatus.ESCALATED and item.status != next(
            i.status for i in items if i.id == item.id
        ):
            repo.update_item_status(item.id, TaskStatus.ESCALATED)
    items = repo.list_checklist_items()

    status_class = {"open": "rs-open", "closed": "rs-closed", "escalated": "rs-escalated"}
    for item in items:
        with st.container(border=True):
            cols = st.columns([5, 2, 2, 2, 2])
            cols[0].markdown(f"**{item.description}**")
            cols[1].caption(f"Owner: {item.owner}")
            cols[2].caption(f"Severity: {item.severity.value}")
            cols[3].caption(f"Due: {item.due_date}")
            status_html = (
                f'<span class="rs-badge {status_class[item.status.value]}">'
                f"{item.status.value.upper()}</span>"
            )
            cols[4].markdown(status_html, unsafe_allow_html=True)
            if item.status == TaskStatus.OPEN or item.status == TaskStatus.ESCALATED:
                if st.button("Mark closed", key=f"close-{item.id}"):
                    repo.update_item_status(item.id, close_item(item).status)
                    st.rerun()
