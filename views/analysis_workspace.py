from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.constants import REVIEW_STATUSES
from src.export_service import ExportService
from ui.components import app_header, badge, chips, empty_state, navigate, section_title


def _flat_frame(records: list[dict[str, Any]], multiline_keys: set[str] | None = None) -> pd.DataFrame:
    multiline_keys = multiline_keys or set()
    rows=[]
    for record in records:
        row={}
        for key,value in record.items():
            if isinstance(value,list):
                row[key] = "\n".join(map(str,value)) if key in multiline_keys else ", ".join(map(str,value))
            elif isinstance(value,dict):
                row[key] = ", ".join(f"{k}: {v}" for k,v in value.items())
            else:
                row[key]=value
        rows.append(row)
    return pd.DataFrame(rows)


def _split(value: Any, multiline: bool = False) -> list[str]:
    if isinstance(value,list): return value
    text=str(value or "")
    parts=text.splitlines() if multiline else text.split(",")
    return [part.strip() for part in parts if part.strip()]


def _apply_table(records: list[dict[str,Any]], edited: pd.DataFrame, list_fields: set[str] | None=None, multiline_fields:set[str]|None=None) -> list[dict[str,Any]]:
    list_fields=list_fields or set(); multiline_fields=multiline_fields or set()
    result=[]
    for idx,row in edited.iterrows():
        base=dict(records[idx]) if idx < len(records) else {}
        for key,value in row.to_dict().items():
            if pd.isna(value) if not isinstance(value,(list,dict)) else False:
                value=""
            if key in list_fields:
                base[key]=_split(value,key in multiline_fields)
            else:
                base[key]=value.item() if hasattr(value,"item") else value
        result.append(base)
    return result


def _load_result(ctx, analysis_id: str) -> dict[str,Any]:
    state_key=f"analysis_result::{analysis_id}"
    if state_key not in st.session_state:
        st.session_state[state_key]=ctx.database.get_analysis(analysis_id)
    return st.session_state[state_key]


def _save_result(ctx, result: dict[str,Any]) -> None:
    ctx.database.save_analysis(result)
    st.session_state[f"analysis_result::{result['analysis_id']}"]=result


def render(ctx) -> None:
    app_header("Analysis Workspace", "Review results and finalize the impact analysis report")
    analyses=ctx.database.list_analyses()
    if not analyses:
        empty_state("No analysis results yet", "Create a Change Request and press Analyze before opening this page.")
        if st.button("Create Change Request", type="primary"):
            navigate("New Change Request")
        return

    # Deduplicate: keep only the latest analysis per CR ID
    # (re-running analysis creates new analysis_id entries for same cr_id)
    _seen: dict[str, dict] = {}
    for item in analyses:
        cr_id = item["cr_id"]
        # list_analyses returns items in insertion order; last one wins = latest
        _seen[cr_id] = item
    analyses = sorted(_seen.values(), key=lambda x: x["cr_id"])

    ids=[item["analysis_id"] for item in analyses]
    default=st.session_state.get("active_analysis_id", ids[0])
    selected=st.selectbox(
        "Analysis Record",
        ids,
        index=ids.index(default) if default in ids else 0,
        format_func=lambda analysis_id: next(f"{item['cr_id']} — {item['title']}" for item in analyses if item['analysis_id']==analysis_id),
    )
    st.session_state["active_analysis_id"]=selected
    result=_load_result(ctx,selected)
    cr=ctx.database.get_change_request(result["cr_id"]) or {}

    st.markdown(
        f"""
        <div class="sf-card">
          <div style="display:grid;grid-template-columns:1fr 2.5fr .8fr .9fr;gap:22px;align-items:center">
            <div><div style="font-size:10px;letter-spacing:.08em;opacity:.6">CR ID</div><div style="font-size:20px;font-weight:750;color:var(--primary)">{cr.get('id','')}</div></div>
            <div><div style="font-size:10px;letter-spacing:.08em;opacity:.6">TITLE</div><div style="font-size:17px;font-weight:720">{cr.get('title','')}</div></div>
            <div><div style="font-size:10px;letter-spacing:.08em;opacity:.6">PRIORITY</div><div style="margin-top:5px">{badge(cr.get('priority',''))}</div></div>
            <div><div style="font-size:10px;letter-spacing:.08em;opacity:.6">STATUS</div><div style="margin-top:5px">{badge(result.get('ba_review_status') if result.get('ba_review_status')!='Draft' else result.get('analysis_status','Analyzed'))}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview, documents, scope, artifacts, suggestions, review = st.tabs([
        "Overview", "Related Documents", "Impact Scope", "Artifacts To Review", "BA Suggestions", "Review & Export"
    ])

    with overview:
        left,right=st.columns([2.25,1])
        with left:
            section_title("Change Request Summary")
            st.write(result.get("summary", ""))
            st.markdown("**Change Description**")
            st.write(cr.get("description", ""))
            info1,info2=st.columns(2)
            info1.markdown(f"<div class='sf-soft-panel'><small>Change Type</small><br><b>{cr.get('change_type','')}</b></div>",unsafe_allow_html=True)
            info2.markdown(f"<div class='sf-soft-panel'><small>Affected Process</small><br><b>{cr.get('affected_process') or 'Pending BA confirmation'}</b></div>",unsafe_allow_html=True)
        with right:
            section_title("Analysis Information")
            st.markdown(
                f"""
                <div class="sf-soft-panel">
                  <div style="margin-bottom:13px"><small>Processing Time</small><br><b>{result.get('processing_time_ms',0):.2f} ms</b></div>
                  <div style="margin-bottom:13px"><small>Related Documents</small><br><b>{len(result.get('retrieved_artefacts',[]))}</b></div>
                  <div style="margin-bottom:13px"><small>Impacted Modules</small><br><b>{len(result.get('impacted_modules',[]))}</b></div>
                  <div><small>Review Status</small><br><b>{result.get('ba_review_status','Draft')}</b></div>
                </div>
                """,unsafe_allow_html=True)


    with documents:
        section_title("Related Project Documents", "Keep relevant documents and annotate items that need review.")
        records=result.get("retrieved_artefacts",[])
        if records:
            frame=_flat_frame(records)
            columns=[c for c in ["selected","rank","document_id","artefact_type","title","bm25_score","matched_keywords","module_ids","retrieval_reason","ba_note"] if c in frame.columns]
            edited=st.data_editor(
                frame[columns],use_container_width=True,hide_index=True,height=430,
                disabled=[c for c in columns if c not in {"selected","ba_note"}],
                column_config={"bm25_score":st.column_config.NumberColumn("Relevance Score",format="%.3f"),"selected":st.column_config.CheckboxColumn("Keep"),"ba_note":st.column_config.TextColumn("BA Note",width="medium")},
                key=f"retrieved_editor_{selected}",
            )
            if st.button("Save Document Selection",key=f"save_docs_{selected}"):
                result["retrieved_artefacts"]=_apply_table(records,edited,list_fields={"matched_keywords","module_ids","related_artifact_ids"})
                selected_ids={x["document_id"] for x in result["retrieved_artefacts"] if x.get("selected",True)}
                for item in result.get("artefacts_to_review",[]): item["selected"]=item.get("document_id") in selected_ids
                _save_result(ctx,result);st.success("Document selection saved.")
        else: empty_state("No matching documents","BA should clarify the request content before proceeding with analysis.")

    with scope:
        section_title("Impacted Modules", "Impact levels are initial suggestions and need BA confirmation.")
        records=result.get("impacted_modules",[])[:5]
        frame=_flat_frame(records)
        if not frame.empty:
            cols=[c for c in ["module_id","module_name","impact_level","impact_reason","evidence","ba_decision","ba_note"] if c in frame.columns]
            edited=st.data_editor(
                frame[cols],use_container_width=True,hide_index=True,height=400,num_rows="dynamic",
                column_config={
                    "impact_level":st.column_config.SelectboxColumn("Impact Level",options=["Low","Medium","High","Critical","Need Review"]),
                    "ba_decision":st.column_config.SelectboxColumn("BA Decision",options=["Need Review","Confirmed","Excluded"]),
                    "ba_note":st.column_config.TextColumn("BA Note",width="large"),
                },key=f"modules_editor_{selected}")
            if st.button("Save Impact Scope",key=f"save_scope_{selected}"):
                result["impacted_modules"]=_apply_table(records,edited,list_fields={"evidence","related_rule"})
                _save_result(ctx,result);st.success("Impact scope saved.")
        else: empty_state("No modules identified","Results need further clarification.")

    with artifacts:
        section_title("Artifacts To Review", "Most relevant artifacts by document group.")
        records=[item for item in result.get("artefacts_to_review",[]) if item.get("selected",True)][:12]
        if not records:
            empty_state("No artifacts to review","Check related documents or clarify the request.")
        else:
            labels={"user_story":"User Story","business_rule":"Business Rule","sop":"SOP","test_case":"Test Case","role":"Role"}
            for group in ["user_story","business_rule","sop","test_case","role"]:
                items=[item for item in records if item.get("artefact_type")==group]
                if not items: continue
                with st.expander(f"{labels[group]} ({len(items)})",expanded=group in {"user_story","business_rule"}):
                    frame=_flat_frame(items)
                    cols=[c for c in ["document_id","title","review_action","retrieval_reason","ba_note"] if c in frame.columns]
                    edited=st.data_editor(frame[cols],use_container_width=True,hide_index=True,key=f"artifact_{group}_{selected}",column_config={"review_action":st.column_config.SelectboxColumn(options=["Review","Update","Create","No Action"]),"ba_note":st.column_config.TextColumn(width="large")})
                    if st.button(f"Save {labels[group]}",key=f"save_art_{group}_{selected}"):
                        updated=_apply_table(items,edited)
                        lookup={x["document_id"]:x for x in updated}
                        result["artefacts_to_review"]=[lookup.get(x.get("document_id"),x) for x in result.get("artefacts_to_review",[])]
                        _save_result(ctx,result);st.success(f"{labels[group]} group saved.")

    with suggestions:
        section_title("Clarification, Risks and Draft Requirements")
        qtab,rtab,dtab=st.tabs(["Questions & Risks","Draft Requirements","Assumptions & Dependencies"])
        with qtab:
            questions=result.get("clarifying_questions",[])[:5]
            risks=result.get("risks",[])[:3]
            st.markdown("**Clarifying Questions**")
            qframe=_flat_frame(questions)
            if not qframe.empty:
                qcols=[c for c in ["question_id","question","reason","answer","status"] if c in qframe.columns]
                qedit=st.data_editor(qframe[qcols],use_container_width=True,hide_index=True,key=f"questions_{selected}",column_config={"answer":st.column_config.TextColumn(width="large"),"status":st.column_config.SelectboxColumn(options=["Open","Answered","Closed"])})
            else: qedit=pd.DataFrame()
            st.markdown("**Risks**")
            rframe=_flat_frame(risks)
            if not rframe.empty:
                rcols=[c for c in ["risk_id","risk_description","risk_level","mitigation_suggestion","ba_status"] if c in rframe.columns]
                redit=st.data_editor(rframe[rcols],use_container_width=True,hide_index=True,key=f"risks_{selected}",column_config={"risk_level":st.column_config.SelectboxColumn(options=["Low","Medium","High"]),"ba_status":st.column_config.SelectboxColumn(options=["Open","Accepted","Mitigated"])})
            else: redit=pd.DataFrame()
            if st.button("Save Questions & Risks",key=f"save_qr_{selected}"):
                if not qedit.empty: result["clarifying_questions"]=_apply_table(questions,qedit)+result.get("clarifying_questions",[])[5:]
                if not redit.empty: result["risks"]=_apply_table(risks,redit)+result.get("risks",[])[3:]
                _save_result(ctx,result);st.success("Questions and risks saved.")
        with dtab:
            st.markdown("**Draft User Stories**")
            stories=result.get("draft_user_stories",[])[:2]
            for idx,story in enumerate(stories):
                story["user_story"]=st.text_area(f"{story.get('story_id','User Story')}",story.get("user_story",""),height=105,key=f"story_{selected}_{idx}")
                ac="\n".join(story.get("acceptance_criteria",[]))
                story["acceptance_criteria"]=_split(st.text_area("Acceptance Criteria",ac,height=115,key=f"ac_{selected}_{idx}"),True)
            st.markdown("**Draft Business Rules**")
            rules=result.get("draft_business_rules",[])[:2]
            for idx,rule in enumerate(rules):
                rule["business_rule"]=st.text_area(rule.get("rule_id","Business Rule"),rule.get("business_rule",""),height=90,key=f"br_{selected}_{idx}")
            st.markdown("**Draft Test Scenarios**")
            tests=result.get("draft_test_scenarios",[])[:5]
            tframe=_flat_frame(tests)
            if not tframe.empty:
                tcols=[c for c in ["test_id","preconditions","test_steps","expected_result","priority"] if c in tframe.columns]
                tedit=st.data_editor(tframe[tcols],use_container_width=True,hide_index=True,key=f"tests_{selected}",column_config={"priority":st.column_config.SelectboxColumn(options=["Low","Medium","High"])})
            else:tedit=pd.DataFrame()
            if st.button("Save Draft Requirements",key=f"save_drafts_{selected}"):
                result["draft_user_stories"]=stories+result.get("draft_user_stories",[])[2:]
                result["draft_business_rules"]=rules+result.get("draft_business_rules",[])[2:]
                if not tedit.empty:result["draft_test_scenarios"]=_apply_table(tests,tedit)+result.get("draft_test_scenarios",[])[5:]
                _save_result(ctx,result);st.success("Draft requirements saved.")
        with rtab:
            st.markdown("**Assumptions**")
            for item in result.get("assumptions",[]): st.markdown(f"- {item}")
            st.markdown("**Dependencies**")
            for item in result.get("dependencies",[]): st.markdown(f"- {item}")

    with review:
        section_title("BA Review")
        left,right=st.columns([1,1.35])
        with left:
            reviewer=st.text_input("Reviewer Name",key=f"reviewer_{selected}")
            status=st.selectbox("Review Status",REVIEW_STATUSES,index=REVIEW_STATUSES.index(result.get("ba_review_status","Draft")) if result.get("ba_review_status","Draft") in REVIEW_STATUSES else 0,key=f"status_{selected}")
            comment=st.text_area("BA Notes",height=145,key=f"comment_{selected}")
            if st.button("Save Review",type="primary",use_container_width=True,key=f"save_review_{selected}"):
                if status=="Confirmed" and not reviewer.strip():
                    st.error("Please enter a Reviewer Name before confirming.")
                else:
                    result["ba_review_status"]=status
                    result["analysis_status"]="Reviewed" if status=="Confirmed" else "Analyzed"
                    _save_result(ctx,result)
                    cr_update=dict(cr);cr_update["status"]="Reviewed" if status=="Confirmed" else "Analyzed";ctx.database.save_change_request(cr_update)
                    ctx.database.save_review(selected,reviewer,status,comment,{"analysis_id":selected,"comment":comment})
                    st.success("BA Review saved.")
        with right:
            st.markdown("**Requirement Traceability Matrix**")
            rtm=result.get("traceability_matrix",[])
            rframe=_flat_frame(rtm)
            if not rframe.empty:
                rcols=[c for c in ["cr_id","rule_id","module_id","artefact_type","artefact_id","test_case_id","impact_level","review_status","ba_note"] if c in rframe.columns]
                rtmedit=st.data_editor(rframe[rcols],use_container_width=True,hide_index=True,height=330,num_rows="dynamic",key=f"rtm_{selected}")
                if st.button("Save Traceability Matrix",key=f"save_rtm_{selected}"):
                    result["traceability_matrix"]=_apply_table(rtm,rtmedit)
                    _save_result(ctx,result);st.success("Traceability Matrix saved.")

        st.divider()
        export=ExportService()
        e1,e2=st.columns(2)
        if e1.button("Prepare Impact Analysis Report",use_container_width=True,key=f"prep_docx_{selected}"):
            path=export.export_docx(cr,result);st.session_state[f"docx_path_{selected}"]=str(path)
        if e2.button("Prepare Traceability Matrix",use_container_width=True,key=f"prep_xlsx_{selected}"):
            path=export.export_rtm_xlsx(cr,result);st.session_state[f"xlsx_path_{selected}"]=str(path)
        d1,d2=st.columns(2)
        docx_path=Path(st.session_state.get(f"docx_path_{selected}",""))
        xlsx_path=Path(st.session_state.get(f"xlsx_path_{selected}",""))
        if docx_path.is_file(): d1.download_button("Download Impact Analysis Report",docx_path.read_bytes(),file_name=docx_path.name,mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",use_container_width=True)
        if xlsx_path.is_file(): d2.download_button("Download Traceability Matrix",xlsx_path.read_bytes(),file_name=xlsx_path.name,mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
