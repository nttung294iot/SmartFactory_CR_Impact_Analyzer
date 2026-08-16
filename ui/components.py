from __future__ import annotations

import html
from typing import Any

import streamlit as st


def app_header(title: str, subtitle: str = "") -> None:
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    st.markdown(
        f"""
        <div class="sf-topbar">
          <div>
            <h1>{safe_title}</h1>
            {f'<p>{safe_subtitle}</p>' if safe_subtitle else ''}
          </div>
          <div class="sf-topbar-mark">SF</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def intro(title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="sf-intro">
          <div>
            <h2>{html.escape(title)}</h2>
            <p>{html.escape(text)}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_title(title: str, icon: str = "") -> None:
    st.markdown(
        f"""
        <div class="sf-card-title">
          <span>{html.escape(icon)}</span>
          {html.escape(title)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="sf-section-title">
          {html.escape(title)}
        </div>
        {f'<div class="sf-section-sub">{html.escape(subtitle)}</div>' if subtitle else ''}
        """,
        unsafe_allow_html=True,
    )


def metric_grid(items: list[dict[str, Any]]) -> None:
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        tone = item.get("tone", "")
        cls = {"danger": "sf-kpi--danger", "success": "sf-kpi--success", "warning": "sf-kpi--warning"}.get(tone, "")
        with col:
            st.markdown(
                f"""
                <div class="sf-kpi {cls}">
                  <div class="sf-kpi-icon">{html.escape(str(item.get('icon', '')))}</div>
                  <div class="sf-kpi-note">{html.escape(str(item.get('note', '')))}</div>
                  <div class="sf-kpi-label">{html.escape(str(item.get('label', '')))}</div>
                  <div class="sf-kpi-value">{html.escape(str(item.get('value', '0')))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def badge(value: str) -> str:
    lowered = str(value).lower()
    if any(key in lowered for key in ["critical", "high", "rejected"]):
        tone = "red"
    elif any(key in lowered for key in ["medium", "clarification", "need review"]):
        tone = "orange"
    elif any(key in lowered for key in ["confirmed", "reviewed", "active", "completed"]):
        tone = "green"
    elif any(key in lowered for key in ["draft", "analyzed", "analysis", "low"]):
        tone = "blue"
    else:
        tone = "gray"
    return f'<span class="sf-badge sf-badge-{tone}">{html.escape(str(value))}</span>'


def chips(values: list[str]) -> None:
    if not values:
        st.caption("No data detected.")
        return
    body = "".join(f'<span class="sf-chip">{html.escape(str(v))}</span>' for v in values)
    st.markdown(f'<div class="sf-chip-wrap">{body}</div>', unsafe_allow_html=True)


def empty_state(title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="sf-empty">
          <b>{html.escape(title)}</b>
          <span>{html.escape(text)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_errors(errors: list[str]) -> None:
    if not errors:
        return
    lines = "\n".join(f"- {e}" for e in errors)
    st.warning(f"Vui lòng điền đầy đủ các trường bắt buộc:\n\n{lines}")


def artifact_type_badge(type_key: str, label: str | None = None) -> str:
    """Return an inline HTML badge styled by artifact type."""
    _labels = {
        "module": "Module", "user_story": "User Story",
        "business_rule": "Business Rule", "test_case": "Test Case",
        "sop": "SOP", "role": "Role",
    }
    display = html.escape(label or _labels.get(type_key, type_key))
    css_class = f"sf-badge sf-badge-type-{type_key}"
    return f'<span class="{css_class}">{display}</span>'


def sf_table(
    rows: list[dict],
    columns: list[dict],
    max_height: int = 420,
) -> None:
    """
    Render a fully themed HTML table consistent with the UI palette.

    Each column dict must have:
        key   – dict key to read from each row
        label – header label to display
    Optional per-column keys:
        td_class   – extra CSS class on <td> (e.g. 'sf-td-id', 'sf-td-muted', 'sf-td-num')
        renderer   – callable(value) -> HTML string; if omitted, value is html-escaped
    """
    header_html = "".join(f"<th>{html.escape(col['label'])}</th>" for col in columns)
    body_parts: list[str] = []
    for row in rows:
        cells = ""
        for col in columns:
            raw = row.get(col["key"], "")
            renderer = col.get("renderer")
            if renderer:
                cell_html = renderer(raw)
            else:
                cell_html = html.escape(str(raw)) if raw not in (None, "") else '<span style="opacity:.35">—</span>'
            td_cls = col.get("td_class", "")
            cells += f'<td class="{td_cls}">{cell_html}</td>'
        body_parts.append(f"<tr>{cells}</tr>")
    body_html = "".join(body_parts)
    st.markdown(
        f"""
        <div class="sf-table-wrap" style="max-height:{max_height}px;overflow-y:auto">
          <table class="sf-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{body_html}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def navigate(page: str) -> None:
    st.session_state["_navigate_to"] = page
    st.rerun()
