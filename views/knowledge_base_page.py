from __future__ import annotations

import html as _html

import streamlit as st

from ui.components import (
    app_header,
    artifact_type_badge,
    empty_state,
    intro,
    section_title,
    sf_table,
)

TYPE_LABELS = {
    "module": "Module",
    "role": "Role",
    "user_story": "User Story",
    "business_rule": "Business Rule",
    "sop": "SOP",
    "test_case": "Test Case",
}


def render(ctx) -> None:
    app_header("Knowledge Base", "Browse business documents and system artifacts")
    intro("Project Artifacts", "Search by name, document type, or related module.")
    kb = ctx.knowledge_base
    modules = {item["id"]: item["title"] for item in kb if item.get("type") == "module"}

    c1, c2, c3 = st.columns([2, 1, 1])
    query = c1.text_input("Search", placeholder="Enter ID, name, or keyword...")
    type_filter = c2.selectbox(
        "Artifact Type",
        ["All"] + list(TYPE_LABELS),
        format_func=lambda v: "All" if v == "All" else TYPE_LABELS[v],
    )
    module_filter = c3.selectbox(
        "Module",
        ["All"] + list(modules),
        format_func=lambda v: "All" if v == "All" else modules[v],
    )

    filtered = []
    q = query.lower().strip()
    for item in kb:
        if type_filter != "All" and item.get("type") != type_filter:
            continue
        if module_filter != "All" and module_filter not in item.get("module_ids", []):
            continue
        haystack = " ".join([
            item.get("id", ""), item.get("title", ""), item.get("description", ""),
            " ".join(item.get("keywords", [])), " ".join(item.get("tags", [])),
        ]).lower()
        if q and q not in haystack:
            continue
        filtered.append(item)

    section_title(f"Artifacts ({len(filtered)})")
    if not filtered:
        empty_state("No documents found", "Try changing the keyword or filters.")
        return

    # Build rows for sf_table
    rows = []
    for item in filtered:
        rows.append({
            "id": item["id"],
            "title": item["title"],
            "type": item.get("type", ""),
            "modules": ", ".join(modules.get(mid, mid) for mid in item.get("module_ids", [])),
            "related": len(item.get("related_artifact_ids", [])),
            "status": item.get("status", "active"),
        })

    sf_table(
        rows,
        columns=[
            {"key": "id",      "label": "ID",             "td_class": "sf-td-id"},
            {"key": "title",   "label": "Name"},
            {
                "key": "type", "label": "Type",
                "renderer": lambda v: artifact_type_badge(v),
            },
            {"key": "modules", "label": "Module",          "td_class": "sf-td-muted"},
            {"key": "related", "label": "Related",         "td_class": "sf-td-num",
             "renderer": lambda v: f'<span style="font-family:\'Fira Code\',monospace;color:var(--text-muted)">{_html.escape(str(v))}</span>'},
            {
                "key": "status", "label": "Status",
                "renderer": lambda v: (
                    '<span class="sf-badge sf-badge-green">active</span>' if v == "active"
                    else f'<span class="sf-badge sf-badge-gray">{_html.escape(str(v))}</span>'
                ),
            },
        ],
        max_height=440,
    )

    selected = st.selectbox(
        "View Artifact",
        [item["id"] for item in filtered],
        format_func=lambda item_id: f"{item_id} — {next(x['title'] for x in filtered if x['id'] == item_id)}",
    )
    detail = next(item for item in filtered if item["id"] == selected)
    with st.container(border=True):
        st.markdown(f"### {detail['id']} — {detail['title']}")
        st.caption(TYPE_LABELS.get(detail["type"], detail["type"]))
        st.write(detail["description"])
        c1, c2 = st.columns(2)
        c1.markdown("**Related Modules**")
        c1.write(", ".join(modules.get(mid, mid) for mid in detail.get("module_ids", [])) or "—")
        c2.markdown("**Related Artifacts**")
        c2.write(", ".join(detail.get("related_artifact_ids", [])) or "—")
