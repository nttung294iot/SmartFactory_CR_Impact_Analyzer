from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.export_service import ExportService
from ui.components import app_header, badge, empty_state, navigate, section_title, sf_table


def render(ctx) -> None:
    app_header("History", "Review saved Change Requests and continue your analysis")
    crs=ctx.database.list_change_requests()
    analyses=ctx.database.list_analyses()
    analysis_by_cr={item["cr_id"]:item for item in analyses}

    c1,c2,c3=st.columns([2,1,1])
    query=c1.text_input("Search",placeholder="Search by CR ID or title...")
    priority=c2.selectbox("Priority",["All","Low","Medium","High","Critical"])
    status=c3.selectbox("Status",["All","Draft","Analyzed","Reviewed"])

    rows=[]
    for cr in crs:
        analysis=analysis_by_cr.get(cr["id"])
        current_status="Reviewed" if analysis and analysis.get("ba_review_status")=="Confirmed" else ("Analyzed" if analysis else "Draft")
        if query and query.lower() not in f"{cr['id']} {cr['title']}".lower(): continue
        if priority!="All" and cr.get("priority")!=priority: continue
        if status!="All" and current_status!=status: continue
        rows.append({"CR ID":cr["id"],"Title":cr["title"],"Created Date":cr.get("request_date",""),"Priority":cr.get("priority",""),"Analysis Status":current_status,"Review Status":analysis.get("ba_review_status","—") if analysis else "—","Impacted Modules":analysis.get("impacted_module_count",0) if analysis else 0})

    section_title(f"Change Requests ({len(rows)})")
    if not rows:
        empty_state("No matching records","Try adjusting the filters or create a new Change Request.")
        return
    sf_table(
        rows,
        columns=[
            {"key": "CR ID",          "label": "CR ID",           "td_class": "sf-td-id"},
            {"key": "Title",          "label": "Title"},
            {"key": "Created Date",   "label": "Date",            "td_class": "sf-td-muted"},
            {"key": "Priority",       "label": "Priority",
             "renderer": lambda v: badge(v)},
            {"key": "Analysis Status","label": "Analysis Status",
             "renderer": lambda v: badge(v)},
            {"key": "Review Status",  "label": "Review Status",
             "renderer": lambda v: badge(v)},
            {"key": "Impacted Modules","label": "Modules",        "td_class": "sf-td-num",
             "renderer": lambda v: f'<span style="font-family:\'Fira Code\',monospace;color:var(--text-muted)">{v}</span>'},
        ],
        max_height=430,
    )

    selected=st.selectbox("Selected Change Request",[row["CR ID"] for row in rows],format_func=lambda cr_id:f"{cr_id} — {next(row['Title'] for row in rows if row['CR ID']==cr_id)}")
    cr=ctx.database.get_change_request(selected)
    analysis_summary=analysis_by_cr.get(selected)
    b1,b2,b3,b4=st.columns(4)
    if b1.button("View / Continue",use_container_width=True):
        if analysis_summary:
            result=ctx.database.get_analysis(analysis_summary["analysis_id"])
            st.session_state["active_analysis_id"]=analysis_summary["analysis_id"]
            st.session_state[f"analysis_result::{analysis_summary['analysis_id']}"]=result
            navigate("Analysis Workspace")
        else:
            st.session_state["cr_form"]=cr
            navigate("New Change Request")
    if b2.button("Re-analyze",use_container_width=True,disabled=not bool(cr)):
        if cr:
            updated=dict(cr);updated["status"]="Analyzed"
            result=ctx.run_analysis(updated)
            st.session_state["active_analysis_id"]=result["analysis_id"]
            st.session_state[f"analysis_result::{result['analysis_id']}"]=result
            navigate("Analysis Workspace")
    if b3.button("Prepare Export",use_container_width=True,disabled=not bool(analysis_summary)):
        result=ctx.database.get_analysis(analysis_summary["analysis_id"])
        export=ExportService();docx=export.export_docx(cr,result);xlsx=export.export_rtm_xlsx(cr,result)
        st.session_state[f"history_docx_{selected}"]=str(docx);st.session_state[f"history_xlsx_{selected}"]=str(xlsx)
    if b4.button("Delete",use_container_width=True):
        st.session_state[f"confirm_delete_{selected}"]=True

    d1,d2=st.columns(2)
    docx=Path(st.session_state.get(f"history_docx_{selected}",""));xlsx=Path(st.session_state.get(f"history_xlsx_{selected}",""))
    if docx.is_file():d1.download_button("Download Report",docx.read_bytes(),file_name=docx.name,mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",use_container_width=True)
    if xlsx.is_file():d2.download_button("Download RTM",xlsx.read_bytes(),file_name=xlsx.name,mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)

    if st.session_state.get(f"confirm_delete_{selected}"):
        st.warning(f"Delete {selected} and all related analysis results?")
        y,n=st.columns(2)
        if y.button("Confirm Delete",type="primary",use_container_width=True):
            ctx.database.delete_change_request(selected);st.session_state.pop(f"confirm_delete_{selected}",None);st.rerun()
        if n.button("Cancel",use_container_width=True):st.session_state.pop(f"confirm_delete_{selected}",None);st.rerun()
