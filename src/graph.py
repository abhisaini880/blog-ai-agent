from src.nodes.orchestrator import orchestrator
from langgraph.graph import StateGraph, START, END
from src.models import State
from src.nodes.worker import worker
from src.nodes.reducer import reducer
from src.nodes.fanout import fanout_to_researchers, fanout_to_writers
from src.nodes.researcher import researcher
from src.nodes.reviewer import plan_review
from langgraph.checkpoint.memory import InMemorySaver


def pre_research(state: State) -> dict:
    """Bridge node: plan approved, fan out to researchers from here."""
    return {}


def research_done(state: State) -> dict:
    """Bridge node: all research merged, fan out to writers from here."""
    return {}


def build_graph():
    graph = StateGraph(State)

    graph.add_node("orchestrator", orchestrator)
    graph.add_node("plan_review", plan_review)
    graph.add_node("pre_research", pre_research)
    graph.add_node("researcher", researcher)
    graph.add_node("research_done", research_done)
    graph.add_node("worker", worker)
    graph.add_node("reducer", reducer)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "plan_review")
    graph.add_conditional_edges("pre_research", fanout_to_researchers, ["researcher"])

    graph.add_edge("researcher", "research_done")
    graph.add_conditional_edges("research_done", fanout_to_writers, ["worker"])
    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", END)

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
