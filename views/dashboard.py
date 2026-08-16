from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from src.constants import SEED_DIR
from src.utils import load_json
from ui.components import app_header, badge, intro, metric_grid, navigate, section_title, sf_table


def render(ctx) -> None:
    app_header("Dashboard", "Overview of change requests and recent analysis results")

    crs = ctx.database.list_change_requests()
    analyses = ctx.database.list_analyses()
    analyzed_cr_ids = {item["cr_id"] for item in analyses}
    reviewed = sum(1 for item in analyses if item.get("ba_review_status") == "Confirmed")
    pending = sum(1 for item in crs if item["id"] not in analyzed_cr_ids)

    left, right = st.columns([1.3, 1])
    with left:
        intro("Processing Overview", "Track and manage Change Requests in the system.")
    with right:
        a, b = st.columns(2)
        if a.button("Load Sample Request", use_container_width=True):
            samples = load_json(SEED_DIR / "sample_change_requests.json", [])
            if samples:
                st.session_state["cr_form"] = samples[0]
                navigate("New Change Request")
        if b.button("＋ New Change Request", type="primary", use_container_width=True):
            st.session_state.pop("cr_form", None)
            navigate("New Change Request")

    metric_grid([
        {"label": "Total Change Requests", "value": len(crs), "icon": "CR", "note": "Total"},
        {"label": "Pending Analysis", "value": pending, "icon": "!", "note": "Awaiting", "tone": "danger" if pending else ""},
        {"label": "Analyzed", "value": len(analyzed_cr_ids), "icon": "◎", "note": "Analyzed"},
        {"label": "Reviewed", "value": reviewed, "icon": "✓", "note": "BA Confirmed", "tone": "success"},
    ])

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    col_recent, col_modules = st.columns([1.75, 1])
    with col_recent:
        section_title("Recent Change Requests")
        if crs:
            rows = []
            analysis_by_cr = {item["cr_id"]: item for item in analyses}
            for item in crs[:5]:
                analysis = analysis_by_cr.get(item["id"])
                rows.append({
                    "CR ID": item["id"],
                    "Title": item["title"],
                    "Priority": item["priority"],
                    "Status": "Reviewed" if analysis and analysis.get("ba_review_status") == "Confirmed" else ("Analyzed" if analysis else "Draft"),
                    "Created Date": item.get("request_date", ""),
                })
            sf_table(
                rows,
                columns=[
                    {"key": "CR ID",       "label": "CR ID",        "td_class": "sf-td-id"},
                    {"key": "Title",       "label": "Title"},
                    {"key": "Priority",    "label": "Priority",
                     "renderer": lambda v: badge(v)},
                    {"key": "Status",      "label": "Status",
                     "renderer": lambda v: badge(v)},
                    {"key": "Created Date","label": "Date",         "td_class": "sf-td-muted"},
                ],
                max_height=300,
            )
            selected = st.selectbox("Quick Open", [item["id"] for item in crs[:5]], format_func=lambda cr_id: f"{cr_id} — {next(x['title'] for x in crs if x['id']==cr_id)}")
            if st.button("View Change Request", use_container_width=True):
                latest = ctx.database.latest_analysis_for_cr(selected)
                if latest:
                    st.session_state["active_analysis_id"] = latest["analysis_id"]
                    st.session_state["active_result"] = latest
                    navigate("Analysis Workspace")
                else:
                    st.session_state["cr_form"] = ctx.database.get_change_request(selected)
                    navigate("New Change Request")
        else:
            st.info("No Change Requests yet. Create your first request or load sample data.")

    with col_modules:
        section_title("Most Impacted Modules")
        counts: Counter[str] = Counter()
        names: dict[str, str] = {}
        for summary in analyses:
            detail = ctx.database.get_analysis(summary["analysis_id"]) or {}
            for module in detail.get("impacted_modules", []):
                if module.get("module_id") == "BA-CONFIRM":
                    continue
                counts[module.get("module_id", "")] += 1
                names[module.get("module_id", "")] = module.get("module_name", module.get("module_id", ""))
        if counts:
            max_value = max(counts.values())
            for module_id, value in counts.most_common(5):
                width = int(value / max_value * 100)
                st.markdown(
                    f"""
                    <div class="sf-rank-row">
                      <div class="sf-rank-head"><b>{names.get(module_id,module_id)}</b><span>{value} CR</span></div>
                      <div class="sf-bar"><i style="width:{width}%"></i></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No analysis results available yet.")
