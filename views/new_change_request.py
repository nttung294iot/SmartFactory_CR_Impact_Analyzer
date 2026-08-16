from __future__ import annotations

from datetime import date

import streamlit as st

from src.constants import CHANGE_TYPES, PRIORITIES, SEED_DIR
from src.utils import load_json
from src.validation import validate_change_request
from ui.components import app_header, card_title, navigate, show_errors


def _samples() -> list[dict]:
    return load_json(SEED_DIR / "sample_change_requests.json", [])


def _safe_date(value: str | None) -> date:
    try:
        return date.fromisoformat(value or "")
    except ValueError:
        return date.today()


def render(ctx) -> None:
    app_header("New Change Request", "Provide the required information before running the impact analysis")
    samples = _samples()
    data = st.session_state.get("cr_form", {})
    cr_id = data.get("id") or ctx.database.next_cr_id()

    with st.container(border=True):
        card_title("Basic Information", "ⓘ")
        c1, c2 = st.columns([1, 2.15])
        c1.text_input("CR ID", value=cr_id, disabled=True)
        title = c2.text_input("Title *", value=data.get("title", ""), placeholder="e.g. Auto-generate Emergency Work Order")
        c1, c2, c3 = st.columns([1.15, 1.15, 1])
        requester = c1.text_input("Requester *", value=data.get("requester", ""), placeholder="Requestor name")
        request_date = c2.date_input("Request Date", value=_safe_date(data.get("request_date")))
        priority = c3.selectbox("Priority *", PRIORITIES, index=PRIORITIES.index(data.get("priority", "Medium")) if data.get("priority", "Medium") in PRIORITIES else 1)
        c1, c2 = st.columns(2)
        department = c1.text_input("Department", value=data.get("department", ""), placeholder="Maintenance / Production")
        change_type = c2.selectbox("Change Type", CHANGE_TYPES, index=CHANGE_TYPES.index(data.get("change_type", "Other")) if data.get("change_type", "Other") in CHANGE_TYPES else len(CHANGE_TYPES)-1)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        card_title("Request Details", "▤")
        description = st.text_area("Change Description *", value=data.get("description", ""), height=125, placeholder="Describe the actor, conditions, timeline, and system behavior required...")
        reason = st.text_area("Business Reason *", value=data.get("reason_for_change", ""), height=90, placeholder="Business problem to be solved")
        c1, c2 = st.columns(2)
        current = c1.text_area("Current Behavior", value=data.get("current_behavior", ""), height=105)
        expected = c2.text_area("Expected Behavior *", value=data.get("expected_behavior", ""), height=105)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        card_title("Initial Scope", "◎")
        c1, c2 = st.columns(2)
        affected_process = c1.text_input("Affected Process", value=data.get("affected_process", ""), placeholder="Condition Monitoring / Work Order...")
        initial_module = c2.selectbox(
            "Expected Module",
            [""] + [item["id"] for item in ctx.knowledge_base if item.get("type") == "module"],
            index=([""] + [item["id"] for item in ctx.knowledge_base if item.get("type") == "module"]).index(data.get("initial_module", "")) if data.get("initial_module", "") in ([""] + [item["id"] for item in ctx.knowledge_base if item.get("type") == "module"]) else 0,
            format_func=lambda value: "Not specified" if not value else f"{value} — {next(item['title'] for item in ctx.knowledge_base if item['id']==value)}",
        )
        c1, c2 = st.columns(2)
        deadline = c1.text_input("Desired Deadline", value=data.get("expected_deadline", ""), placeholder="YYYY-MM-DD or Sprint")
        business_value = c2.text_input("Business Value", value=data.get("business_value", ""), placeholder="Reduce downtime, SLA control...")
        notes = st.text_area("Notes", value=data.get("attachment_note", ""), height=80, placeholder="Notes or related documents")

    payload = {
        "id": cr_id,
        "title": title,
        "requester": requester,
        "request_date": request_date.isoformat(),
        "department": department,
        "priority": priority,
        "change_type": change_type,
        "initial_category": data.get("initial_category", "Other"),
        "description": description,
        "reason_for_change": reason,
        "current_behavior": current,
        "expected_behavior": expected,
        "business_value": business_value,
        "affected_process": affected_process,
        "initial_module": initial_module,
        "expected_deadline": deadline,
        "attachment_note": notes,
        "status": "Draft",
    }

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    a, b, c, d = st.columns([1.05, 1, 1, 1.25])
    if a.button("Load Sample", use_container_width=True):
        selected = st.session_state.get("sample_selector", samples[0]["id"] if samples else "")
        if samples:
            st.session_state["cr_form"] = next((item for item in samples if item["id"] == selected), samples[0])
            st.rerun()
    if b.button("Reset", use_container_width=True):
        st.session_state.pop("cr_form", None)
        st.rerun()
    if c.button("Save Draft", use_container_width=True):
        ok, errors, model = validate_change_request(payload)
        show_errors(errors)
        if ok and model:
            ctx.database.save_change_request(model.model_dump())
            st.session_state["cr_form"] = model.model_dump()
            st.success("Change Request saved as Draft.")
    if d.button("Analyze", type="primary", use_container_width=True):
        analyze_payload = dict(payload)
        analyze_payload["status"] = "Analyzed"
        ok, errors, model = validate_change_request(analyze_payload)
        show_errors(errors)
        if ok and model:
            with st.spinner("Processing Change Request..."):
                result = ctx.run_analysis(model.model_dump())
            st.session_state["active_analysis_id"] = result["analysis_id"]
            st.session_state["active_result"] = result
            st.session_state.pop("cr_form", None)
            navigate("Analysis Workspace")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.selectbox(
        "Sample Request",
        [item["id"] for item in samples],
        format_func=lambda item_id: f"{item_id} — {next(item['title'] for item in samples if item['id']==item_id)}",
        key="sample_selector",
        help="Select a sample scenario and press Load Sample.",
    )
