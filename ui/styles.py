from __future__ import annotations

import streamlit as st

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&family=Fira+Code:wght@400;500;600&display=swap');

:root {
  --primary: #6366F1;
  --primary-glow: rgba(99, 102, 241, 0.4);
  --cyan: #06B6D4;
  --cyan-bright: #38BDF8;
  --cyan-glow: rgba(6, 182, 212, 0.4);
  
  --bg-dark: #0B0F17;
  --bg-card: #151D2A;
  --bg-input: #0F172A;
  --surface-border: #263347;
  --surface-border-bright: #334155;
  
  --text-primary: #FFFFFF;
  --text-body: #F1F5F9;
  --text-muted: #94A3B8;
  --text-dim: #64748B;
  
  --danger: #EF4444;
  --danger-bg: rgba(239, 68, 68, 0.16);
  --danger-border: #EF4444;
  
  --success: #10B981;
  --success-bg: rgba(16, 185, 129, 0.16);
  --success-border: #10B981;
  
  --warning: #F59E0B;
  --warning-bg: rgba(245, 158, 11, 0.16);
  --warning-border: #F59E0B;
}

/* Base Body & App Background */
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--text-body);
}

.stApp {
  background: var(--bg-dark);
  background-image: 
    radial-gradient(circle at 12% 12%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
    radial-gradient(circle at 88% 80%, rgba(6, 182, 212, 0.12) 0%, transparent 45%);
  background-attachment: fixed;
  color: var(--text-body);
}




/* Universal Text Hierarchy */
p, span, label, li, td, th {
  color: var(--text-body);
}

h1, h2, h3, h4, h5, h6, 
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
  color: var(--text-primary) !important;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

caption, small, .stCaption {
  color: var(--text-muted) !important;
}

/* Keyframe Animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes statusDotPulse {
  0% { opacity: 0.5; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0.5; transform: scale(0.9); }
}

/* Streamlit Header / Toolbar Controls */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"] { visibility: hidden; }

header[data-testid="stHeader"] {
  background: transparent !important;
  z-index: 99999 !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[aria-label="Expand sidebar"],
button[aria-label="Collapse sidebar"],
header[data-testid="stHeader"] button {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  color: var(--cyan-bright) !important;
  background: #151D2A !important;
  border: 1px solid var(--surface-border-bright) !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
  backdrop-filter: blur(12px) !important;
  transition: all 0.2s ease !important;
}

[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
  transform: scale(1.05);
  border-color: var(--cyan-bright) !important;
  box-shadow: 0 0 15px var(--cyan-glow) !important;
}

/* Sidebar Theme — let Streamlit control width in collapsed state */
[data-testid="stSidebar"] {
  background: #090E17 !important;
  border-right: 1px solid var(--surface-border) !important;
  box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Sidebar EXPANDED — apply custom fixed width */
[data-testid="stSidebar"][aria-expanded="true"] {
  min-width: 280px !important;
  max-width: 280px !important;
}

/* Sidebar COLLAPSED — release width entirely so stMain can expand */
[data-testid="stSidebar"][aria-expanded="false"] {
  min-width: 0 !important;
  max-width: 0 !important;
  width: 0 !important;
  overflow: hidden !important;
  border-right: none !important;
  box-shadow: none !important;
}

/* Main content area — smooth transition when sidebar toggles */
[data-testid="stMain"],
section[data-testid="stMain"] {
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  flex: 1 1 auto !important;
  min-width: 0 !important;
}

/* block-container fills available width with smooth transition */
.block-container {
  max-width: 100% !important;
  width: 100% !important;
  padding: 1.5rem 2.5rem 4rem !important;
  box-sizing: border-box !important;
  transition: padding 0.3s ease !important;
  animation: fadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

[data-testid="stSidebar"] > div:first-child {
  padding: 1.4rem 0 1rem;
  display: flex !important;
  flex-direction: column !important;
  height: 100% !important;
}


.sf-brand {
  padding: 0 22px 24px;
  border-bottom: 1px solid var(--surface-border);
  margin-bottom: 20px;
}

.sf-brand-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'Fira Code', monospace;
  font-size: 10px;
  letter-spacing: 0.1em;
  color: var(--cyan-bright);
  background: rgba(6, 182, 212, 0.15);
  border: 1px solid rgba(6, 182, 212, 0.35);
  padding: 3px 9px;
  border-radius: 999px;
  margin-bottom: 12px;
}

.sf-brand-badge i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--cyan-bright);
  display: inline-block;
  animation: statusDotPulse 2s infinite ease-in-out;
}

.sf-brand-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #FFFFFF;
  line-height: 1.1;
}

.sf-brand-subtitle {
  font-size: 11.5px;
  color: var(--text-muted);
  margin-top: 6px;
  font-weight: 500;
}

.sf-nav-label {
  font-family: 'Fira Code', monospace;
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  padding: 0 22px 10px;
  font-weight: 600;
}

[data-testid="stSidebar"] div[role="radiogroup"] {
  gap: 4px;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
  padding: 12px 18px;
  margin: 0 10px;
  border-radius: 10px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  background: transparent;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--surface-border);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(6, 182, 212, 0.25) 100%);
  border: 1px solid var(--cyan-bright);
  box-shadow: 0 4px 16px rgba(6, 182, 212, 0.2);
}

[data-testid="stSidebar"] div[role="radiogroup"] label p {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-body) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
  color: #FFFFFF !important;
  font-weight: 700;
}

.sf-sidebar-card {
  margin: 22px 14px 0;
  padding: 16px;
  border-radius: 14px;
  background: var(--bg-card);
  border: 1px solid var(--surface-border);
  position: relative;
  overflow: hidden;
}

.sf-sidebar-card b {
  display: block;
  font-size: 12px;
  color: var(--text-primary);
  margin-bottom: 6px;
  font-weight: 700;
}

.sf-sidebar-card span {
  font-size: 11.5px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Topbar Header */
.sf-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 18px 24px;
  margin-bottom: 26px;
  background: var(--bg-card);
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.sf-topbar h1 {
  font-size: 26px;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary) !important;
}

.sf-topbar p {
  font-size: 13.5px;
  color: var(--text-muted);
  margin: 4px 0 0;
}

.sf-topbar-mark {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  font-family: 'Orbitron', sans-serif;
  font-weight: 800;
  font-size: 16px;
  box-shadow: 0 0 20px var(--cyan-glow);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Intro & Section Titles */
.sf-intro h2 {
  font-size: 19px;
  font-weight: 750;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.sf-intro p {
  font-size: 13.5px;
  color: var(--text-muted);
  margin: 0;
}

.sf-card {
  background: var(--bg-card);
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  margin-bottom: 20px;
  transition: all 0.25s ease;
}

.sf-card:hover {
  border-color: var(--surface-border-bright);
}

.sf-card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 750;
  color: var(--text-primary);
  padding-bottom: 14px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--surface-border);
}

.sf-card-title span {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(6, 182, 212, 0.15);
  color: var(--cyan-bright);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.sf-section-title {
  font-size: 18px;
  font-weight: 750;
  color: var(--text-primary);
  margin: 24px 0 8px;
}

.sf-section-sub {
  font-size: 12.5px;
  color: var(--text-muted);
  margin-top: -4px;
  margin-bottom: 16px;
}

/* KPI Cards */
.sf-kpi {
  min-height: 145px;
  background: var(--bg-card);
  border: 1px solid var(--surface-border);
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.sf-kpi:hover {
  transform: translateY(-2px);
  border-color: var(--cyan-bright);
}

.sf-kpi-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.2);
  border: 1px solid rgba(99, 102, 241, 0.4);
  color: #A5B4FC;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
}

.sf-kpi-label {
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 600;
  margin-top: 16px;
}

.sf-kpi-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 30px;
  line-height: 1.1;
  font-weight: 800;
  color: var(--text-primary);
  margin-top: 6px;
}

.sf-kpi-note {
  position: absolute;
  top: 20px; right: 18px;
  font-size: 10.5px;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.06);
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--surface-border);
}

.sf-kpi--danger .sf-kpi-icon { background: var(--danger-bg); border-color: var(--danger-border); color: #F87171; }
.sf-kpi--success .sf-kpi-icon { background: var(--success-bg); border-color: var(--success-border); color: #34D399; }
.sf-kpi--warning .sf-kpi-icon { background: var(--warning-bg); border-color: var(--warning-border); color: #FBBF24; }

/* Badges & Chips */
.sf-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  font-family: 'Fira Code', monospace;
}

.sf-badge-blue { background: rgba(56, 189, 248, 0.18); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.4); }
.sf-badge-red { background: rgba(248, 113, 113, 0.18); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.4); }
.sf-badge-orange { background: rgba(251, 191, 36, 0.18); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.4); }
.sf-badge-green { background: rgba(52, 211, 153, 0.18); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.4); }
.sf-badge-gray { background: rgba(148, 163, 184, 0.18); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.35); }

.sf-chip-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
.sf-chip {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.16);
  color: #C7D2FE;
  border: 1px solid rgba(99, 102, 241, 0.35);
  font-size: 11.5px;
  font-weight: 600;
}

/* Impact Rank Bar */
.sf-rank-row { margin: 14px 0; }
.sf-rank-head { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-body); margin-bottom: 6px; }
.sf-rank-head b { font-weight: 600; color: var(--text-primary); }
.sf-rank-head span { color: var(--cyan-bright); font-family: 'Fira Code', monospace; font-weight: 700; }
.sf-bar { height: 8px; border-radius: 999px; background: rgba(255, 255, 255, 0.1); overflow: hidden; }
.sf-bar > i { display: block; height: 100%; background: linear-gradient(90deg, var(--primary), var(--cyan)); border-radius: 999px; }

/* ==========================================================================
   STREAMLIT FORM CONTROLS, INPUTS, DISABLED FIELDS & PLACEHOLDERS (CRITICAL FIXES)
   ========================================================================== */

/* Widget Labels */
[data-testid="stWidgetLabel"] p, label p, label {
  font-size: 12.5px !important;
  font-weight: 700 !important;
  color: #E2E8F0 !important;
}

/* Normal Inputs & Textareas */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
div[data-baseweb="input"] input,
textarea {
  border-radius: 10px !important;
  border: 1px solid var(--surface-border-bright) !important;
  background: var(--bg-input) !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stDateInput"] input:focus,
textarea:focus {
  border-color: var(--cyan-bright) !important;
  box-shadow: 0 0 14px rgba(6, 182, 212, 0.35) !important;
}

/* CRITICAL FIX FOR DISABLED INPUT FIELDS & TEXT AREAS (Prevent sunken dark text) */
input:disabled,
textarea:disabled,
select:disabled,
[disabled],
input[disabled],
textarea[disabled],
[aria-disabled="true"],
.stTextInput input:disabled,
.stNumberInput input:disabled,
.stDateInput input:disabled,
div[data-baseweb="input"] input:disabled {
  color: #38BDF8 !important;
  -webkit-text-fill-color: #38BDF8 !important;
  background-color: #151F30 !important;
  border: 1px solid var(--surface-border-bright) !important;
  opacity: 1 !important;
  font-weight: 600 !important;
  cursor: not-allowed !important;
}

/* CRITICAL FIX FOR PLACEHOLDERS IN SEARCH & TEXT INPUTS */
input::placeholder,
textarea::placeholder,
[data-baseweb="input"] input::placeholder,
.stTextInput input::placeholder {
  color: #94A3B8 !important;
  -webkit-text-fill-color: #94A3B8 !important;
  opacity: 1 !important;
}

/* ================================================================
   SELECTBOX — Input trigger box
   ================================================================ */
div[data-baseweb="select"] > div {
  border-radius: 10px !important;
  border: 1px solid var(--surface-border-bright) !important;
  background: var(--bg-input) !important;
  color: #FFFFFF !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: var(--cyan-bright) !important;
  box-shadow: 0 0 14px rgba(6, 182, 212, 0.3) !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] [data-testid="stSelectbox"] {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}
/* Chevron arrow icon */
div[data-baseweb="select"] svg {
  fill: var(--text-muted) !important;
}

/* ================================================================
   DROPDOWN POPOVER — the floating list portal
   Streamlit teleports this outside stApp so we need :root-level rules
   ================================================================ */

/* Outer portal wrapper */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
div[data-baseweb="popover"],
ul[data-baseweb="menu"],
div[data-baseweb="menu"] {
  background: #131C2A !important;
  border: 1px solid var(--surface-border-bright) !important;
  border-radius: 12px !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(56,189,248,.12) !important;
  overflow: hidden !important;
  backdrop-filter: blur(12px) !important;
}

/* All children inside the popover (BaseUI creates nested divs) */
[data-baseweb="popover"] *,
[data-baseweb="menu"] * {
  background-color: transparent !important;
  color: #F1F5F9 !important;
  -webkit-text-fill-color: #F1F5F9 !important;
}

/* Individual option items */
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"],
div[data-baseweb="menu"] li,
div[data-baseweb="menu"] div[role="option"] {
  color: #E2E8F0 !important;
  -webkit-text-fill-color: #E2E8F0 !important;
  background: transparent !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  padding: 10px 16px !important;
  border-radius: 0 !important;
  cursor: pointer !important;
  transition: background 0.12s, color 0.12s !important;
}

/* Hovered & selected option */
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="menu"] li[aria-selected="true"],
[data-baseweb="menu"] [role="option"][aria-selected="true"],
div[data-baseweb="menu"] li:hover,
div[data-baseweb="menu"] div[role="option"]:hover,
div[data-baseweb="menu"] li[aria-selected="true"] {
  background: rgba(6, 182, 212, 0.12) !important;
  color: var(--cyan-bright) !important;
  -webkit-text-fill-color: var(--cyan-bright) !important;
}

/* Highlighted/focused option (keyboard nav) */
[data-baseweb="menu"] li[data-highlighted],
[data-baseweb="menu"] [role="option"][data-highlighted] {
  background: rgba(99, 102, 241, 0.15) !important;
  color: #C7D2FE !important;
  -webkit-text-fill-color: #C7D2FE !important;
}

/* Dividers between groups */
[data-baseweb="menu"] hr {
  border-color: var(--surface-border) !important;
  margin: 4px 0 !important;
}

/* Search input inside multi-select dropdowns */
[data-baseweb="menu"] input[type="text"] {
  background: #0F172A !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
  border: 1px solid var(--surface-border-bright) !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  font-size: 13px !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
  border-radius: 10px !important;
  min-height: 44px;
  font-weight: 700 !important;
  border: 1px solid var(--surface-border-bright) !important;
  background: #1E293B !important;
  color: #FFFFFF !important;
  transition: all 0.2s ease !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--cyan-bright) !important;
  color: #FFFFFF !important;
  background: #263347 !important;
  box-shadow: 0 4px 16px rgba(6, 182, 212, 0.25) !important;
}

button[kind="primary"] {
  background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 100%) !important;
  color: #FFFFFF !important;
  border: 0 !important;
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.35) !important;
}

button[kind="primary"]:hover {
  box-shadow: 0 8px 28px rgba(6, 182, 212, 0.5) !important;
  transform: translateY(-1px);
}

/* High Contrast DataFrames */
[data-testid="stDataFrame"], .stDataFrame {
  border: 1px solid var(--surface-border-bright) !important;
  border-radius: 14px !important;
  overflow: hidden;
  background: #151D2A !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* AG Grid Cell & Header Text — force palette colors */
.stDataFrame .ag-root-wrapper,
.stDataFrame .ag-root,
.stDataFrame .ag-body-viewport {
  background: #151D2A !important;
}
.stDataFrame .ag-header {
  background: #0F172A !important;
  border-bottom: 1px solid var(--surface-border-bright) !important;
}
.stDataFrame .ag-header-cell-text {
  color: var(--text-muted) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}
.stDataFrame .ag-cell {
  color: var(--text-body) !important;
  font-size: 13px !important;
  border-color: var(--surface-border) !important;
}
.stDataFrame .ag-row {
  background: transparent !important;
  border-bottom: 1px solid var(--surface-border) !important;
}
.stDataFrame .ag-row:hover {
  background: rgba(99, 102, 241, 0.08) !important;
}
.stDataFrame .ag-row-even {
  background: rgba(255, 255, 255, 0.02) !important;
}
.stDataFrame .ag-cell-value,
.stDataFrame .ag-cell span,
.stDataFrame .ag-cell div {
  color: var(--text-body) !important;
}
/* Remove blue hyperlink color from any linked cells */
.stDataFrame a, .stDataFrame .ag-cell a {
  color: var(--cyan-bright) !important;
  text-decoration: none !important;
}

/* sf-table — custom themed HTML table */
.sf-table-wrap { overflow-x: auto; margin: 10px 0 18px; border-radius: 14px; border: 1px solid var(--surface-border-bright); background: #151D2A; box-shadow: 0 10px 30px rgba(0,0,0,.3); }
.sf-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.sf-table thead tr { background: #0F172A; border-bottom: 1px solid var(--surface-border-bright); }
.sf-table thead th { padding: 11px 14px; text-align: left; font-family: 'Fira Code', monospace; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); white-space: nowrap; }
.sf-table tbody tr { border-bottom: 1px solid var(--surface-border); transition: background .15s; }
.sf-table tbody tr:last-child { border-bottom: none; }
.sf-table tbody tr:hover { background: rgba(99,102,241,.07); }
.sf-table tbody tr:nth-child(even) { background: rgba(255,255,255,.02); }
.sf-table tbody tr:nth-child(even):hover { background: rgba(99,102,241,.07); }
.sf-table td { padding: 10px 14px; color: var(--text-body); vertical-align: middle; }
.sf-table td.sf-td-id { font-family: 'Fira Code', monospace; font-size: 11.5px; color: var(--cyan-bright); font-weight: 600; white-space: nowrap; }
.sf-table td.sf-td-muted { color: var(--text-muted); font-size: 12px; }
.sf-table td.sf-td-num { font-family: 'Fira Code', monospace; font-size: 12px; color: var(--text-muted); text-align: right; }
/* Type-specific badge colors for artifact types */
.sf-badge-type-module    { background: rgba(99,102,241,.18); color: #A5B4FC; border: 1px solid rgba(99,102,241,.4); }
.sf-badge-type-user_story { background: rgba(6,182,212,.15); color: #38BDF8; border: 1px solid rgba(6,182,212,.4); }
.sf-badge-type-business_rule { background: rgba(245,158,11,.15); color: #FBBF24; border: 1px solid rgba(245,158,11,.4); }
.sf-badge-type-test_case { background: rgba(52,211,153,.15); color: #34D399; border: 1px solid rgba(52,211,153,.4); }
.sf-badge-type-sop       { background: rgba(251,191,36,.12); color: #FCD34D; border: 1px solid rgba(251,191,36,.35); }
.sf-badge-type-role      { background: rgba(148,163,184,.15); color: #CBD5E1; border: 1px solid rgba(148,163,184,.35); }

/* Container Border Wrapper */
[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--surface-border) !important;
  border-radius: 16px !important;
  background: var(--bg-card) !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

/* Tabs High Contrast */
[data-baseweb="tab-list"] {
  gap: 6px;
  background: #0F172A;
  padding: 6px;
  border-radius: 12px;
  border: 1px solid var(--surface-border-bright);
  overflow-x: auto;
}

[data-baseweb="tab"] {
  border-radius: 9px;
  padding: 10px 18px;
  height: auto;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-muted);
  white-space: nowrap;
}

[data-baseweb="tab"]:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

[data-baseweb="tab"][aria-selected="true"] {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.35) 0%, rgba(6, 182, 212, 0.3) 100%);
  color: #FFFFFF;
  border: 1px solid var(--cyan-bright);
}

/* Expanders & Alerts */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--surface-border-bright) !important;
  border-radius: 12px !important;
}

[data-testid="stExpander"] summary span {
  color: var(--text-primary) !important;
  font-weight: 700 !important;
}

[data-testid="stAlert"] {
  border-radius: 12px !important;
  background: #151D2A !important;
  border: 1px solid var(--surface-border-bright) !important;
}

[data-testid="stAlert"] p {
  color: #FFFFFF !important;
}

hr { border-color: var(--surface-border) !important; }

.sf-empty {
  padding: 40px 24px;
  text-align: center;
  border: 1px dashed var(--surface-border-bright);
  border-radius: 16px;
  background: var(--bg-card);
}

.sf-empty b {
  display: block;
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.sf-empty span {
  font-size: 13px;
  color: var(--text-muted);
}

.sf-footer {
  margin-top: 45px;
  border-top: 1px solid var(--surface-border);
  padding-top: 20px;
  font-size: 11px;
  color: var(--text-dim);
  text-align: center;
}

/* Sidebar Author Card — pinned to bottom of sidebar */
.sf-author-spacer {
  flex: 1 1 auto;
  min-height: 40px;
}

.sf-author-card {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 10px 16px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.07);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-left: 3px solid var(--cyan-bright);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.sf-author-card:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.4);
  border-left-color: var(--cyan-bright);
}

.sf-author-avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--cyan) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 0.05em;
  box-shadow: 0 0 12px var(--cyan-glow);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.sf-author-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.sf-author-name {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sf-author-id {
  font-family: 'Fira Code', monospace;
  font-size: 9px;
  color: var(--cyan-bright);
  font-weight: 600;
  letter-spacing: 0.08em;
  opacity: 0.9;
  margin-bottom: 4px;
}

.sf-author-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.sf-author-tag {
  font-size: 9px;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1px 6px;
  border-radius: 999px;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .block-container { padding-left: 1.2rem; padding-right: 1.2rem; }
  .sf-topbar { flex-direction: column; align-items: flex-start; }
  .sf-kpi { min-height: 130px; }
}
</style>
"""

def apply_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    # Second pass: inject styles at body level to capture BaseUI portals
    # (Streamlit teleports dropdown menus outside stApp, so we must style from body root)
    st.markdown("""
<style>
body, body * {
  --dropdown-bg: #131C2A;
  --dropdown-border: #334155;
  --dropdown-item: #E2E8F0;
  --dropdown-hover-bg: rgba(6,182,212,0.12);
  --dropdown-hover-color: #38BDF8;
  --dropdown-selected-bg: rgba(99,102,241,0.18);
  --dropdown-selected-color: #A5B4FC;
}

/* Target BaseUI popover containers at body level */
body [data-baseweb="popover"],
body [data-baseweb="popover"] > div,
body div[data-baseweb="popover"] {
  background: var(--dropdown-bg) !important;
  border: 1px solid var(--dropdown-border) !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 50px rgba(0,0,0,0.75), 0 0 0 1px rgba(56,189,248,0.1) !important;
  overflow: hidden !important;
}

body [data-baseweb="menu"],
body ul[data-baseweb="menu"],
body div[data-baseweb="menu"] {
  background: var(--dropdown-bg) !important;
  border-radius: 12px !important;
}

body [data-baseweb="menu"] *,
body [data-baseweb="popover"] * {
  background-color: transparent !important;
  color: var(--dropdown-item) !important;
  -webkit-text-fill-color: var(--dropdown-item) !important;
}

body [data-baseweb="menu"] li,
body [data-baseweb="menu"] [role="option"] {
  color: var(--dropdown-item) !important;
  -webkit-text-fill-color: var(--dropdown-item) !important;
  background: transparent !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  padding: 10px 16px !important;
  transition: background 0.12s ease, color 0.12s ease !important;
  cursor: pointer !important;
}

body [data-baseweb="menu"] li:hover,
body [data-baseweb="menu"] [role="option"]:hover {
  background: var(--dropdown-hover-bg) !important;
  color: var(--dropdown-hover-color) !important;
  -webkit-text-fill-color: var(--dropdown-hover-color) !important;
}

body [data-baseweb="menu"] li[aria-selected="true"],
body [data-baseweb="menu"] [role="option"][aria-selected="true"] {
  background: var(--dropdown-selected-bg) !important;
  color: var(--dropdown-selected-color) !important;
  -webkit-text-fill-color: var(--dropdown-selected-color) !important;
  font-weight: 700 !important;
}

body [data-baseweb="menu"] hr {
  border-color: #263347 !important;
  margin: 4px 0 !important;
}
</style>
""", unsafe_allow_html=True)
