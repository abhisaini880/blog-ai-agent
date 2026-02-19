from src.nodes.orchestrator import orchestrator
from langgraph.graph import StateGraph, START, END
from src.models import State
from src.nodes.worker import worker
from src.nodes.reducer import reducer
from src.nodes.fanout import fanout_to_researchers, fanout_to_writers
from src.nodes.researcher import researcher
from src.nodes.reviewer import plan_review
from src.nodes.image_generator import image_generator
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Send


def pre_research(state: State) -> dict:
    """Bridge node: plan approved, fan out to researchers from here."""
    return {}


def research_done(state: State) -> dict:
    """Bridge node: all research merged, fan out to writers from here."""
    return {}


def route_after_pre_research(state: State) -> list[Send] | str:
    sends = fanout_to_researchers(state)
    if sends:
        return sends
    return "research_done"


def build_graph():
    graph = StateGraph(State)

    graph.add_node("orchestrator", orchestrator)
    graph.add_node("plan_review", plan_review)
    graph.add_node("pre_research", pre_research)
    graph.add_node("researcher", researcher)
    graph.add_node("research_done", research_done)
    graph.add_node("worker", worker)
    graph.add_node("image_generator", image_generator)
    graph.add_node("reducer", reducer)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "plan_review")
    graph.add_conditional_edges(
        "pre_research", route_after_pre_research, ["researcher", "research_done"]
    )

    graph.add_edge("researcher", "research_done")
    graph.add_conditional_edges("research_done", fanout_to_writers, ["worker"])
    graph.add_edge("worker", "image_generator")
    graph.add_edge("image_generator", "reducer")
    graph.add_edge("reducer", END)

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
