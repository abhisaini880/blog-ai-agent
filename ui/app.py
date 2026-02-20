"""Inkwell — AI-powered technical blog generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import re
import streamlit as st
import uuid
import time
import pandas as pd
from collections import defaultdict

from src.graph import build_graph
from langgraph.types import Command
from ui.styles import PROGRESS_CSS, PAGE_CSS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"


# ---------------------------------------------------------------------------
# Async helper — one persistent loop, no nesting needed
# ---------------------------------------------------------------------------


def _get_loop() -> asyncio.AbstractEventLoop:
    """Return a persistent background event loop, creating it if needed."""
    if "_event_loop" not in st.session_state:
        loop = asyncio.new_event_loop()
        st.session_state._event_loop = loop
    return st.session_state._event_loop


def run_async(coro):
    """Run a coroutine on the persistent loop (safe to call from Streamlit's thread)."""
    return _get_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

STAGES = [
    {"label": "Planning blog structure", "nodes": {"orchestrator"}},
    {"label": "Reviewing plan", "nodes": {"plan_review"}},
    {
        "label": "Researching sections",
        "nodes": {"pre_research", "researcher", "research_done"},
    },
    {"label": "Writing sections", "nodes": {"worker"}},
    {"label": "Generating diagrams", "nodes": {"image_generator"}},
    {"label": "Assembling blog", "nodes": {"reducer"}},
    {"label": "Evaluating quality", "nodes": {"evaluator", "rewriter"}},
]

IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def node_to_stage(node_name: str) -> int | None:
    for i, stage in enumerate(STAGES):
        if node_name in stage["nodes"]:
            return i
    return None


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Inkwell", layout="wide", initial_sidebar_state="expanded"
)
# Hide stale idle form in phases that don't use forms
_phase = st.session_state.get("phase", "idle")
_phase_css = (
    '[data-testid="stForm"] { display: none !important; }'
    if _phase not in ("idle", "reviewing")
    else ""
)
st.markdown(
    f"<style>{PAGE_CSS}\n{PROGRESS_CSS}\n{_phase_css}</style>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

DEFAULTS = {
    "phase": "idle",
    "graph": None,
    "config": None,
    "topic": "",
    "plan": None,
    "plan_display": "",
    "completed_stages": [],
    "active_stage": None,
    "stage_details": {},
    "final_blog": "",
    "token_usage": [],
    "resume_value": None,
    "error": None,
    "generation_time": 0.0,
    "viewing_file": None,
}

for key, val in DEFAULTS.items():
    st.session_state.setdefault(key, val)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def reset_session():
    for key in DEFAULTS:
        if key in st.session_state:
            del st.session_state[key]


WRITING_SCENE_HTML = (
    '<div class="writing-scene">'
    '<span class="writing-pen">&#9998;</span>'
    '<div class="writing-paper">'
    '<div class="paper-line"></div>'
    '<div class="paper-line"></div>'
    '<div class="paper-line"></div>'
    '<div class="paper-line"></div>'
    "</div>"
    '<div class="writing-label">Writing your blog...</div>'
    "</div>"
)


def render_progress(
    completed: list[int], active: int | None, details: dict, show_writing: bool = False
):
    """Render vertical progress list (Claude-style) with optional writing animation."""
    parts = ['<div class="progress-list">']
    for i, stage in enumerate(STAGES):
        if i in completed:
            cls = "completed"
            icon = "<span>&#10003;</span>"
        elif i == active:
            cls = "active"
            icon = '<div class="progress-dot"></div>'
        else:
            cls = "pending"
            icon = '<div class="progress-circle"></div>'

        detail = ""
        if i in details and details[i]:
            detail = f'<span class="progress-detail">{details[i]}</span>'

        parts.append(
            f'<div class="progress-item {cls}">'
            f'<div class="progress-icon">{icon}</div>'
            f'<div class="progress-text">{stage["label"]}{detail}</div>'
            f"</div>"
        )
    parts.append("</div>")
    if show_writing:
        parts.append(WRITING_SCENE_HTML)
    return "".join(parts)


def render_blog_markdown(markdown_text: str):
    """Render markdown with local images via st.image()."""
    parts = IMAGE_PATTERN.split(markdown_text)
    i = 0
    while i < len(parts):
        if i + 2 < len(parts):
            text_before = parts[i]
            alt_text = parts[i + 1]
            img_path = parts[i + 2]

            if text_before.strip():
                st.markdown(text_before)

            resolved = OUTPUT_DIR / img_path
            if not resolved.exists():
                resolved = PROJECT_ROOT / img_path
            if resolved.exists():
                st.image(str(resolved), caption=alt_text)
            else:
                st.caption(f"[Image not found: {img_path}]")
            i += 3
        else:
            if parts[i].strip():
                st.markdown(parts[i])
            i += 1


def render_plan_details(plan):
    """Render the plan in the Plan tab."""
    if not plan:
        st.write("No plan data available.")
        return
    st.markdown(f"**{plan.blog_title}**")
    for i, task in enumerate(plan.tasks, 1):
        tags = []
        if task.needs_research:
            tags.append("research")
        if task.needs_image:
            tags.append("diagram")
        tag_str = f'  `{"  ".join(tags)}`' if tags else ""
        st.markdown(f"**{i}. {task.title}**{tag_str}")
        st.markdown(
            f'<span style="color:#666;font-size:0.85rem">&nbsp;&nbsp;{task.brief}</span>',
            unsafe_allow_html=True,
        )


def render_token_usage(usage: list):
    if not usage:
        st.write("No token usage data available.")
        return

    by_node = defaultdict(lambda: {"input": 0, "output": 0})
    total_in = total_out = 0
    for t in usage:
        by_node[t.node]["input"] += t.input_tokens
        by_node[t.node]["output"] += t.output_tokens
        total_in += t.input_tokens
        total_out += t.output_tokens

    c1, c2, c3 = st.columns(3)
    c1.metric("Input Tokens", f"{total_in:,}")
    c2.metric("Output Tokens", f"{total_out:,}")
    c3.metric("Total", f"{total_in + total_out:,}")

    rows = [
        {
            "Node": node,
            "Input": f"{c['input']:,}",
            "Output": f"{c['output']:,}",
            "Total": f"{c['input'] + c['output']:,}",
        }
        for node, c in sorted(by_node.items())
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def _update_progress_for_chunk(
    node_name, chunk_data, placeholder, researcher_count, worker_count, totals
):
    stage_idx = node_to_stage(node_name)
    if stage_idx is None:
        return researcher_count, worker_count

    for s in range(stage_idx):
        if s not in st.session_state.completed_stages:
            st.session_state.completed_stages.append(s)
    st.session_state.active_stage = stage_idx

    total_researchers, total_workers = totals
    if node_name == "researcher":
        researcher_count += 1
        if total_researchers:
            st.session_state.stage_details[2] = (
                f"{researcher_count}/{total_researchers}"
            )
    elif node_name == "research_done":
        if 2 not in st.session_state.completed_stages:
            st.session_state.completed_stages.append(2)
        st.session_state.active_stage = 3
    elif node_name == "worker":
        worker_count += 1
        if total_workers:
            st.session_state.stage_details[3] = f"{worker_count}/{total_workers}"
    elif node_name == "image_generator":
        st.session_state.stage_details[4] = "rendering"
    elif node_name == "reducer":
        st.session_state.stage_details[5] = "finalizing"
    elif node_name == "evaluator":
        feedback = chunk_data.get("evaluator", {}).get("eval_feedback", "")
        if not feedback:
            st.session_state.stage_details[6] = "passed"
        else:
            brief = feedback[:60] + "..." if len(feedback) > 60 else feedback
            st.session_state.stage_details[6] = brief
    elif node_name == "rewriter":
        st.session_state.stage_details[6] = "revising..."

    html = render_progress(
        st.session_state.completed_stages,
        st.session_state.active_stage,
        st.session_state.stage_details,
        show_writing=True,
    )
    placeholder.markdown(html, unsafe_allow_html=True)
    return researcher_count, worker_count


def _handle_stream_end(app, config):
    state = run_async(app.aget_state(config))
    if state.next:
        interrupt_data = state.tasks[0].interrupts[0].value
        st.session_state.plan_display = interrupt_data.get("plan", "")
        st.session_state.plan = state.values.get("plan")
        st.session_state.completed_stages = [0]
        st.session_state.active_stage = 1
        st.session_state.phase = "reviewing"
        return True
    else:
        final_values = state.values
        st.session_state.final_blog = final_values.get("final", "")
        st.session_state.token_usage = final_values.get("token_usage", [])
        st.session_state.completed_stages = list(range(len(STAGES)))
        st.session_state.active_stage = None
        st.session_state.phase = "done"
        return False


def run_stream(input_data, progress_placeholder):
    app = st.session_state.graph
    config = st.session_state.config
    plan = st.session_state.plan

    total_researchers = sum(1 for t in plan.tasks if t.needs_research) if plan else 0
    total_workers = len(plan.tasks) if plan else 0
    totals = (total_researchers, total_workers)
    researcher_count = 0
    worker_count = 0

    async def _stream():
        nonlocal researcher_count, worker_count
        async for chunk in app.astream(
            input_data, config=config, stream_mode="updates"
        ):
            node_name = list(chunk.keys())[0]
            researcher_count, worker_count = _update_progress_for_chunk(
                node_name, chunk, progress_placeholder, researcher_count, worker_count, totals
            )

    run_async(_stream())
    return _handle_stream_end(app, config)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="sidebar-brand">Inkwell</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-tagline">AI Tech Blog Writer</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    if st.button("New blog", width="stretch", type="primary", icon=":material/add:"):
        reset_session()
        st.rerun()

    st.markdown("---")

    blog_files = (
        sorted(OUTPUT_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        if OUTPUT_DIR.exists()
        else []
    )

    if blog_files:
        st.caption("Recent")
        with st.container(height=400):
            for f in blog_files:
                title = f.stem.replace("_", " ").replace(":", "").strip()
                display = (title[0].upper() + title[1:]) if title else title
                display = display[:40] + "..." if len(display) > 40 else display
                if st.button(display, key=f"h_{f.name}", width="stretch"):
                    st.session_state.viewing_file = str(f)
                    st.session_state.phase = "viewing"
                    st.rerun()

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

# ------------------------------------------------------------------
# IDLE
# ------------------------------------------------------------------
if st.session_state.phase == "idle":
    for _ in range(4):
        st.markdown("")

    st.markdown(
        "<h4 style='text-align:center'>What do you want to write about?</h4>",
        unsafe_allow_html=True,
    )
    with st.form("topic_form"):
        topic = st.text_input(
            "Topic",
            placeholder="e.g., Event Driven Architecture in Microservices",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Generate", type="primary")

    if submitted and topic.strip():
        st.session_state.pop("topic_nudge", None)
        st.session_state.topic = topic.strip()
        st.session_state.phase = "planning"
        st.rerun()

    # Show friendly nudge if topic was rejected
    nudge = st.session_state.pop("topic_nudge", None)
    if nudge:
        st.markdown(
            '<p style="text-align:center;color:#b05a3a;font-size:0.85rem;margin-top:0.5rem">'
            "I'm a tech blog specialist — software, systems, architecture, and all things engineering. "
            "I'm still learning about the rest of the world, but I promise to branch out once I've "
            "mastered distributed systems. Until then, try a technical topic!"
            "</p>",
            unsafe_allow_html=True,
        )

    # Topic suggestions — single row
    st.markdown("")
    st.markdown(
        '<p style="color:#aaa;font-size:0.78rem;margin-bottom:0.4rem">Or try one of these</p>',
        unsafe_allow_html=True,
    )
    SUGGESTIONS = [
        "Event Driven Architecture",
        "OAuth 2.0 Deep Dive",
        "Kubernetes Networking",
        "Rate Limiter Design",
    ]
    sug_cols = st.columns(len(SUGGESTIONS))
    for c, s in zip(sug_cols, SUGGESTIONS):
        with c:
            if st.button(s, key=f"sug_{s[:10]}"):
                st.session_state.topic = s
                st.session_state.phase = "planning"
                st.rerun()

# ------------------------------------------------------------------
# VIEWING (past blog)
# ------------------------------------------------------------------
elif st.session_state.phase == "viewing":
    filepath = Path(st.session_state.viewing_file)
    if filepath.exists():
        content = filepath.read_text(encoding="utf-8")
        render_blog_markdown(content)
        st.markdown("---")
        st.download_button(
            "Download Markdown",
            data=content,
            file_name=filepath.name,
            mime="text/markdown",
        )
    else:
        st.error("File not found.")

# ------------------------------------------------------------------
# PLANNING
# ------------------------------------------------------------------
elif st.session_state.phase == "planning":
    progress_placeholder = st.empty()
    progress_placeholder.markdown(
        render_progress([], 0, {}, show_writing=True), unsafe_allow_html=True
    )

    # Lazy init — build graph after progress is already visible
    if st.session_state.graph is None:
        st.session_state.graph = build_graph()
        st.session_state.config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    try:
        start_time = time.time()

        async def _plan_stream():
            app = st.session_state.graph
            config = st.session_state.config
            async for chunk in app.astream(
                {"topic": st.session_state.topic},
                config=config,
                stream_mode="updates",
            ):
                node_name = list(chunk.keys())[0]
                stage_idx = node_to_stage(node_name)
                if stage_idx is not None:
                    st.session_state.active_stage = stage_idx
                    if stage_idx not in st.session_state.completed_stages:
                        st.session_state.completed_stages.append(stage_idx)
                progress_placeholder.markdown(
                    render_progress(
                        st.session_state.completed_stages,
                        st.session_state.active_stage,
                        {},
                        show_writing=True,
                    ),
                    unsafe_allow_html=True,
                )

        run_async(_plan_stream())

        state = run_async(st.session_state.graph.aget_state(st.session_state.config))
        if state.next:
            interrupt_data = state.tasks[0].interrupts[0].value
            st.session_state.plan_display = interrupt_data.get("plan", "")
            st.session_state.plan = state.values.get("plan")
            st.session_state.completed_stages = [0]
            st.session_state.active_stage = 1
            st.session_state.phase = "reviewing"
            st.session_state.generation_time = time.time() - start_time
            st.rerun()
        else:
            # Topic rejected by guard — go back to idle with a friendly nudge
            topic_error = state.values.get("topic_error", "")
            if topic_error:
                st.session_state.topic_nudge = topic_error
                st.session_state.graph = None
                st.session_state.config = None
                st.session_state.phase = "idle"
                st.rerun()

    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.phase = "error"
        st.rerun()

# ------------------------------------------------------------------
# REVIEWING
# ------------------------------------------------------------------
elif st.session_state.phase == "reviewing":
    plan = st.session_state.plan

    # Build the entire review UI as a single HTML block
    parts = []

    # Progress bar
    parts.append(
        render_progress(
            st.session_state.completed_stages,
            st.session_state.active_stage,
            st.session_state.stage_details,
        )
    )

    # Plan review card
    parts.append('<div class="plan-review">')
    parts.append("<h4>Review the plan</h4>")

    if plan:
        parts.append(f'<p class="plan-title">{plan.blog_title}</p>')
        for i, task in enumerate(plan.tasks, 1):
            tag_html = ""
            if task.needs_research:
                tag_html += '<span class="plan-tag research">research</span>'
            if task.needs_image:
                tag_html += '<span class="plan-tag diagram">diagram</span>'
            parts.append(
                f'<div class="plan-section">'
                f'<div class="section-header">'
                f'<span class="section-num">{i}.</span>'
                f'<span class="section-title">{task.title}</span>'
                f"{tag_html}"
                f"</div>"
                f'<p class="section-brief">{task.brief}</p>'
                f"</div>"
            )
    else:
        parts.append(f"<pre>{st.session_state.plan_display}</pre>")

    parts.append("</div>")

    st.markdown("".join(parts), unsafe_allow_html=True)

    st.markdown("")

    # Interactive controls — centered to match card width
    _, ctrl_col, _ = st.columns([1, 3, 1])
    with ctrl_col:
        c1, c2 = st.columns([1, 2])
        with c1:
            approve = st.button("Approve plan", type="primary", width="stretch")
        with c2:
            with st.form("feedback_form", clear_on_submit=True):
                feedback_text = st.text_input(
                    "feedback",
                    placeholder="Press Enter to revise...",
                    label_visibility="collapsed",
                )
                revise = st.form_submit_button("Revise")

    if approve:
        st.session_state.resume_value = {"action": "approve"}
        st.session_state.completed_stages = [0, 1]
        st.session_state.active_stage = 2
        st.session_state.stage_details = {}
        st.session_state.phase = "streaming"
        st.rerun()
    elif revise and feedback_text.strip():
        st.session_state.resume_value = {
            "action": "reject",
            "feedback": feedback_text.strip(),
        }
        st.session_state.completed_stages = []
        st.session_state.active_stage = 0
        st.session_state.stage_details = {}
        st.session_state.phase = "streaming"
        st.rerun()

# ------------------------------------------------------------------
# STREAMING
# ------------------------------------------------------------------
elif st.session_state.phase == "streaming":
    progress_placeholder = st.empty()
    progress_placeholder.markdown(
        render_progress(
            st.session_state.completed_stages,
            st.session_state.active_stage,
            st.session_state.stage_details,
            show_writing=True,
        ),
        unsafe_allow_html=True,
    )

    try:
        start_time = time.time()

        run_stream(
            Command(resume=st.session_state.resume_value),
            progress_placeholder,
        )

        elapsed = time.time() - start_time
        st.session_state.generation_time += elapsed
        st.rerun()

    except Exception as e:
        st.session_state.error = str(e)
        st.session_state.phase = "error"
        st.rerun()

# ------------------------------------------------------------------
# DONE
# ------------------------------------------------------------------
elif st.session_state.phase == "done":
    blog = st.session_state.final_blog
    plan = st.session_state.plan
    gen_time = st.session_state.generation_time

    # Stats
    word_count = len(blog.split())
    section_count = len(plan.tasks) if plan else 0
    research_count = sum(1 for t in plan.tasks if t.needs_research) if plan else 0
    diagram_count = sum(1 for t in plan.tasks if t.needs_image) if plan else 0

    title = plan.blog_title if plan else st.session_state.topic

    total_tokens = sum(t.total_tokens for t in st.session_state.token_usage)

    meta_items = [f"{word_count:,} words", f"{section_count} sections"]
    if research_count:
        meta_items.append(f"{research_count} researched")
    if diagram_count:
        meta_items.append(f"{diagram_count} diagrams")
    meta_items.append(f"{total_tokens:,} tokens")
    meta_items.append(f"{gen_time:.0f}s")

    meta_html = ' <span class="done-sep">&middot;</span> '.join(
        f"<span>{m}</span>" for m in meta_items
    )

    st.markdown(
        '<div class="done-header">'
        '<div class="done-check">&#10003;</div>'
        f'<p class="done-title">{title}</p>'
        f'<div class="done-meta">{meta_html}</div>'
        "</div>"
        '<hr class="done-divider">',
        unsafe_allow_html=True,
    )

    # Blog content
    render_blog_markdown(blog)

    # Bottom bar
    st.markdown("---")
    filename = st.session_state.topic.lower().replace(" ", "_") + ".md"
    st.download_button(
        "Download Markdown",
        data=blog,
        file_name=filename,
        mime="text/markdown",
        icon=":material/download:",
    )

# ------------------------------------------------------------------
# ERROR
# ------------------------------------------------------------------
elif st.session_state.phase == "error":
    st.error(f"Something went wrong: {st.session_state.error}")
    if st.button("Try Again"):
        reset_session()
        st.rerun()
