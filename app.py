"""RegSense — thin UI orchestration only. All logic lives in regsense/."""
import streamlit as st

from regsense.config import load_config
from regsense.persistence.db import get_connection
from regsense.persistence.repository import Repository
from regsense.ui.circulars_view import render_circulars
from regsense.ui.checklist_view import render_checklist
from regsense.ui.gap_view import render_gaps
from regsense.ui.sidebar import render_sidebar
from regsense.ui.styles import CSS

st.set_page_config(page_title="RegSense", page_icon="⚖️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

config = load_config()
conn = get_connection()
repo = Repository(conn)

render_sidebar(config, repo)

st.title("RegSense")
st.caption("Agentic compliance copilot for SEBI intermediaries — synthetic demo")

tab1, tab2, tab3 = st.tabs(["Circulars", "Gap Analysis", "Checklist"])
with tab1:
    render_circulars(repo)
with tab2:
    render_gaps(repo)
with tab3:
    render_checklist(config, repo)
