from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.app_context import AppContext
from src.constants import APP_NAME, APP_SHORT_NAME, APP_SUBTITLE, DISCLAIMER
from src.logging_service import configure_logging
from ui.styles import apply_styles
from views import analysis_workspace, dashboard, history_page, knowledge_base_page, new_change_request

configure_logging()
st.set_page_config(page_title=APP_NAME, page_icon="🏭", layout="wide", initial_sidebar_state="expanded")
apply_styles()


@st.cache_resource
def get_context() -> AppContext:
    return AppContext()


ctx = get_context()
ctx.refresh()

PAGES = {
    "Dashboard": ("▦   Dashboard", dashboard.render),
    "New Change Request": ("⊕   New Change Request", new_change_request.render),
    "Analysis Workspace": ("▣   Analysis Workspace", analysis_workspace.render),
    "Knowledge Base": ("▤   Knowledge Base", knowledge_base_page.render),
    "History": ("◷   History", history_page.render),
}

if "_navigate_to" in st.session_state:
    st.session_state["nav_selection"] = st.session_state.pop("_navigate_to")
if "nav_selection" not in st.session_state or st.session_state["nav_selection"] not in PAGES:
    st.session_state["nav_selection"] = "Dashboard"

with st.sidebar:
    st.markdown(
        f"""
        <div class="sf-brand">
          <div class="sf-brand-title">{APP_SHORT_NAME}</div>
          <div class="sf-brand-subtitle">{APP_SUBTITLE}</div>
        </div>
        <div class="sf-nav-label">Navigation</div>
        """,
        unsafe_allow_html=True,
    )
    page_key = st.radio(
        "Navigation",
        list(PAGES),
        format_func=lambda key: PAGES[key][0],
        key="nav_selection",
        label_visibility="collapsed",
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if st.button("⚡  + New Analysis", use_container_width=True, type="primary"):
        st.session_state["_navigate_to"] = "New Change Request"
        st.rerun()
    st.markdown("<div class='sf-author-spacer'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="sf-author-card">
          <div class="sf-author-avatar">NT</div>
          <div class="sf-author-info">
            <div class="sf-author-name">Nguyen Thanh Tung</div>
            <div class="sf-author-id">N22DCCI042</div>
            <div class="sf-author-tags">
              <span class="sf-author-tag">PTITHCM</span>
              <span class="sf-author-tag">BA Intern · FPT Software</span>
            </div>
          </div>
        </div>
    """, unsafe_allow_html=True)

PAGES[page_key][1](ctx)

