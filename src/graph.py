from src.nodes.orchestrator import orchestrator
from langgraph.graph import StateGraph, START, END
from src.models import State
from src.nodes.worker import worker
from src.nodes.reducer import reducer
from src.nodes.fanout import fanout_to_researchers, fanout_to_writers
from src.nodes.researcher import researcher
from src.nodes.reviewer import plan_review
from src.nodes.image_generator import image_generator
from src.nodes.topic_guard import topic_guard
from src.nodes.evaluator import evaluator
from src.nodes.rewriter import rewriter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Send


def pre_research(state: State) -> dict:
    """Bridge node: plan approved, fan out to researchers from here."""
    return {}


def research_done(state: State) -> dict:
    """Bridge node: all research merged, fan out to writers from here."""
    return {}


def route_after_guard(state: State) -> str:
    if state.get("topic_error"):
        return END
    return "orchestrator"


def route_after_pre_research(state: State) -> list[Send] | str:
    sends = fanout_to_researchers(state)
    if sends:
        return sends
    return "research_done"


def route_after_eval(state: State) -> str:
    if not state.get("eval_feedback"):
        return END
    if state.get("eval_count", 0) >= 2:
        return END
    return "rewriter"


def build_graph():
    graph = StateGraph(State)

    graph.add_node("topic_guard", topic_guard)
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("plan_review", plan_review)
    graph.add_node("pre_research", pre_research)
    graph.add_node("researcher", researcher)
    graph.add_node("research_done", research_done)
    graph.add_node("worker", worker)
    graph.add_node("image_generator", image_generator)
    graph.add_node("reducer", reducer)
    graph.add_node("evaluator", evaluator)
    graph.add_node("rewriter", rewriter)

    graph.add_edge(START, "topic_guard")
    graph.add_conditional_edges(
        "topic_guard", route_after_guard, ["orchestrator", END]
    )
    graph.add_edge("orchestrator", "plan_review")
    graph.add_conditional_edges(
        "pre_research", route_after_pre_research, ["researcher", "research_done"]
    )
    graph.add_edge("researcher", "research_done")
    graph.add_conditional_edges("research_done", fanout_to_writers, ["worker"])
    graph.add_edge("worker", "image_generator")
    graph.add_edge("image_generator", "reducer")
    graph.add_edge("reducer", "evaluator")
    graph.add_conditional_edges(
        "evaluator", route_after_eval, ["rewriter", END]
    )
    graph.add_edge("rewriter", "evaluator")

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
