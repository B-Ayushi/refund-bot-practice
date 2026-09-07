import sys
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

import streamlit as st
from travel_planner.ui.pages.history import render_history
from travel_planner.ui.pages.planner import render_planner
from travel_planner.ui.pages.preferences import render_preferences
from travel_planner.ui.utils.session_state import initialize_state

st.set_page_config(page_title="Intelligent Travel Planner", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --ink: #17211f; --muted: #52615c; --mint: #c8eadb; --coral: #c9503f; --paper: #f1f4f0; --panel: #ffffff; --line: #c9d4ce; }
[data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
[data-testid="stAppViewContainer"] * { color: var(--ink); }
[data-testid="stSidebar"] { background: #dce8e0; border-right: 1px solid #b9cbc0; }
[data-testid="stSidebar"] * { color: #17211f !important; }
[data-testid="stSidebarNav"] { display: none; }
.block-container { max-width: 1280px; padding-top: 2.5rem; }
h1, h2, h3, p, label, [data-testid="stCaptionContainer"] { color: var(--ink) !important; letter-spacing: 0; }
[data-testid="stCaptionContainer"] { color: var(--muted) !important; }
.stage { display: flex; align-items: center; gap: .45rem; padding: .55rem .6rem; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-size: .78rem; min-height: 2.4rem; }
.stage-icon { width: 1.35rem; height: 1.35rem; display: inline-flex; align-items: center; justify-content: center; border-radius: 50%; background: #e6eee9; color: var(--ink); font-weight: 700; }
.stage-passed { border-color: #85c9a5; background: #f0fbf5; }.stage-passed .stage-icon { color: #167348; background: #c9f0df; }
.stage-warning { border-color: #e2b166; background: #fff8eb; }.stage-warning .stage-icon { color: #9a5d00; background: #ffe0a8; }
.stage-failed { border-color: #e99b8c; background: #fff1ee; }.stage-failed .stage-icon { color: #a43b29; background: #ffd0c7; }
[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); padding: .8rem; border-radius: 8px; }
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input { background: #ffffff; color: var(--ink) !important; border: 1px solid #9fb1a6; }
[data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder { color: #65736d !important; opacity: 1; }
button[kind="primary"] { background: var(--coral) !important; border-color: var(--coral) !important; color: #ffffff !important; }
button[kind="secondary"] { background: #ffffff !important; border-color: #9fb1a6 !important; color: var(--ink) !important; }
[data-testid="stAlert"] { color: var(--ink); }
</style>
""", unsafe_allow_html=True)

initialize_state()

with st.sidebar:
    st.markdown("# ✦ Travel Planner")
    st.caption("A visible multi-agent planning workspace")
    page = st.radio("Workspace", ["Planner", "History", "Preferences"], label_visibility="collapsed")
    st.divider()
    st.session_state.developer_mode = st.checkbox("Developer Mode", value=st.session_state.developer_mode)
    st.caption("Session memory is local to this browser session.")

if page == "Planner":
    st.markdown("# Make room for somewhere else")
    render_planner()
elif page == "History":
    render_history()
else:
    render_preferences()
