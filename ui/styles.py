PAGE_CSS = """
/* Hide Streamlit chrome */
header {display: none !important;}
footer {display: none !important;}

/* Hide stale elements from previous phase instantly */
[data-stale="true"] {
    display: none !important;
}

/* Prevent Streamlit's whole-app dimming during reruns */
.stApp[data-is-stale="true"],
.stApp[data-is-stale] {
    opacity: 1 !important;
}

/* Keep non-stale containers visible (the :not guard lets stale ones hide) */
[data-testid="stAppViewContainer"]:not([data-stale="true"]),
[data-testid="stMain"]:not([data-stale="true"]),
[data-testid="stVerticalBlock"]:not([data-stale="true"]),
[data-testid="stVerticalBlockBorderWrapper"]:not([data-stale="true"]) {
    opacity: 1 !important;
    transition: none !important;
}

/* Reduce main content top padding */
.stMainBlockContainer,
[data-testid="stAppViewBlockContainer"],
.block-container {
    padding-top: 1.5rem !important;
}

/* Sidebar — fixed, no scroll, no collapse */
section[data-testid="stSidebar"] {
    padding-top: 0 !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 rem !important;
}

section[data-testid="stSidebar"] > div {
    overflow: hidden !important;
}

/* Hide any sidebar collapse/expand toggle */
[data-testid*="ollaps"] {
    display: none !important;
}

section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] button[kind="headerNoPadding"],
[data-testid="baseButton-header"],
[data-testid="baseButton-headerNoPadding"] {
    display: none !important;
}

section[data-testid="stSidebar"] .sidebar-brand {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2c2c2c;
    padding: 0.25rem 0;
    letter-spacing: -0.3px;
}

section[data-testid="stSidebar"] .sidebar-tagline {
    font-size: 0.75rem;
    color: #999;
    margin-bottom: 0.75rem;
}

/* New blog button — subtle accent fill */
section[data-testid="stSidebar"] button[data-testid*="rimary"],
section[data-testid="stSidebar"] button[kind="primary"] {
    border: 1.5px solid rgba(201, 100, 66, 0.25) !important;
    background: rgba(201, 100, 66, 0.06) !important;
    color: #b05a3a !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.45rem 0.65rem !important;
    letter-spacing: 0.01em !important;
}

section[data-testid="stSidebar"] button[data-testid*="rimary"]:hover,
section[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: rgba(201, 100, 66, 0.12) !important;
    border-color: rgba(201, 100, 66, 0.4) !important;
    color: #944b30 !important;
}

/* History buttons — target via secondary type (default) */
section[data-testid="stSidebar"] button[data-testid*="econdary"],
section[data-testid="stSidebar"] button[kind="secondary"] {
    text-align: left !important;
    font-weight: 400 !important;
    font-size: 0.8rem !important;
    padding: 0.35rem 0.65rem !important;
    border: none !important;
    background: transparent !important;
    color: #666 !important;
    border-radius: 6px !important;
    max-height: 2rem !important;
    line-height: 1.2 !important;
    overflow: hidden !important;
}

section[data-testid="stSidebar"] button[data-testid*="econdary"] p,
section[data-testid="stSidebar"] button[data-testid*="econdary"] span,
section[data-testid="stSidebar"] button[kind="secondary"] p,
section[data-testid="stSidebar"] button[kind="secondary"] span {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

section[data-testid="stSidebar"] button[data-testid*="econdary"]:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: rgba(0, 0, 0, 0.05) !important;
    color: #222 !important;
}

/* Scrollable history container — strip all borders */
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
}

/* Suggestion pill buttons on idle page (main area secondary buttons) */
[data-testid="stMain"] button[data-testid*="econdary"],
[data-testid="stMain"] button[kind="secondary"] {
    border: 1px solid #e5e0d8 !important;
    background: #faf9f6 !important;
    color: #999 !important;
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    border-radius: 16px !important;
    padding: 0.25rem 0.7rem !important;
    white-space: nowrap !important;
}

[data-testid="stMain"] button[data-testid*="econdary"]:hover,
[data-testid="stMain"] button[kind="secondary"]:hover {
    background: #f0efe9 !important;
    color: #666 !important;
    border-color: #d5d0c8 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e5e5e0;
    padding: 0.75rem;
    border-radius: 8px;
}

[data-testid="stMetricLabel"] {
    color: #888 !important;
}

/* Hide "Press Enter to apply" overlay on text inputs */
[data-testid="InputInstructions"] {
    display: none !important;
}

/* Hide feedback form submit button — Enter submits the form */
button[kind="secondaryFormSubmit"] {
    display: none !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
}

.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
}
"""

PROGRESS_CSS = """
.progress-list {
    padding: 0.5rem 0;
    margin: 0.5rem auto 1.25rem;
    width: fit-content;
}

.progress-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 7px 0;
}

.progress-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* Completed */
.progress-item.completed .progress-icon {
    color: #6b8f6b;
    font-size: 0.85rem;
    font-weight: 700;
}

.progress-item.completed .progress-text {
    color: #888;
    font-size: 0.875rem;
}

/* Active */
.progress-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: #c96442;
    animation: dot-pulse 1.4s ease-in-out infinite;
}

@keyframes dot-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

.progress-item.active .progress-text {
    color: #2c2c2c;
    font-size: 0.875rem;
    font-weight: 500;
}

/* Pending */
.progress-circle {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    border: 1.5px solid #d0d0d0;
}

.progress-item.pending .progress-text {
    color: #c0c0c0;
    font-size: 0.875rem;
}

.progress-detail {
    color: #aaa;
    font-size: 0.78rem;
    margin-left: 6px;
}

/* Step transition — completed items fade in smoothly */
.progress-item.completed {
    animation: stepIn 0.35s ease-out forwards;
}

@keyframes stepIn {
    from { opacity: 0.2; transform: translateX(-4px); }
    to   { opacity: 1;   transform: translateX(0); }
}

/* Writing scene */
.writing-scene {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0;
    margin: 0.5rem auto 0.5rem;
    width: fit-content;
    position: relative;
    top: -8px;
}

.writing-paper {
    width: 48px;
    height: 58px;
    background: #fff;
    border: 1px solid #e0ddd5;
    border-radius: 2px;
    box-shadow: 1px 1px 6px rgba(0,0,0,0.05);
    padding: 8px 5px;
    position: relative;
    overflow: hidden;
}

.paper-line {
    height: 1.5px;
    background: #d8cfc2;
    border-radius: 1px;
    margin-bottom: 6px;
    width: 0%;
    animation: writeLine 2.4s ease-in-out infinite;
}

.paper-line:nth-child(1) { animation-delay: 0s; }
.paper-line:nth-child(2) { animation-delay: 0.5s; }
.paper-line:nth-child(3) { animation-delay: 1.0s; }
.paper-line:nth-child(4) { animation-delay: 1.5s; }

@keyframes writeLine {
    0%   { width: 0%;   opacity: 1; }
    40%  { width: 88%;  opacity: 1; }
    75%  { width: 88%;  opacity: 1; }
    95%  { width: 0%;   opacity: 0.3; }
    100% { width: 0%;   opacity: 1; }
}

.writing-pen {
    font-size: 1.4rem;
    display: inline-block;
    position: relative;
    top: -4px;
    margin-right: 2px;
    transform-origin: bottom right;
    animation: penMove 2.4s ease-in-out infinite;
}

@keyframes penMove {
    0%   { transform: rotate(-40deg) translate(0px,  0px); }
    10%  { transform: rotate(-35deg) translate(3px,  2px); }
    20%  { transform: rotate(-40deg) translate(6px,  0px); }
    30%  { transform: rotate(-36deg) translate(9px,  2px); }
    40%  { transform: rotate(-40deg) translate(12px, 0px); }
    55%  { transform: rotate(-40deg) translate(12px, 0px); }
    70%  { transform: rotate(-40deg) translate(0px,  8px); }
    80%  { transform: rotate(-36deg) translate(3px,  10px); }
    90%  { transform: rotate(-40deg) translate(8px,  8px); }
    100% { transform: rotate(-40deg) translate(0px,  0px); }
}

.writing-label {
    flex-basis: 100%;
    color: #bbb;
    font-size: 0.78rem;
    margin-top: 6px;
    font-style: italic;
}

/* ---- Plan review card ---- */
.plan-review {
    max-width: 680px;
    margin: 1.5rem auto 0;
    padding: 1.5rem 2rem;
    background: #faf9f6;
    border: 1px solid #e8e5df;
    border-radius: 10px;
}

.plan-review h4 {
    margin: 0 0 0.75rem;
    font-size: 0.9rem;
    color: #999;
    font-weight: 500;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.plan-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #2c2c2c;
    margin: 0 0 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e8e5df;
}

.plan-section {
    margin-bottom: 0.9rem;
}

.section-header {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin-bottom: 3px;
}

.section-num {
    color: #bbb;
    font-size: 0.82rem;
    font-weight: 600;
    min-width: 16px;
}

.section-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: #2c2c2c;
}

.plan-tag {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 600;
    padding: 1px 8px;
    border-radius: 10px;
    margin-left: 4px;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.plan-tag.research {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.plan-tag.diagram {
    background: rgba(201, 100, 66, 0.1);
    color: #c96442;
}

.section-brief {
    color: #777;
    font-size: 0.82rem;
    line-height: 1.5;
    padding-left: 22px;
    margin: 0;
}

/* ---- Done page ---- */
.done-header {
    max-width: 780px;
    margin: 2rem auto 0.75rem;
    text-align: center;
}

.done-check {
    color: #6b8f6b;
    font-size: 1.5rem;
    margin-bottom: 0.35rem;
}

.done-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #2c2c2c;
    margin: 0 0 0.6rem;
    line-height: 1.35;
}

.done-meta {
    color: #999;
    font-size: 0.78rem;
}

.done-sep {
    color: #d0d0d0;
    margin: 0 2px;
}

.done-divider {
    max-width: 780px;
    margin: 0.75rem auto 1.5rem;
    border: none;
    border-top: 1px solid #e8e5df;
}
"""
