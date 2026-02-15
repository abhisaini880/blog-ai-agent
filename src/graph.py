from src.nodes.orchestrator import orchestrator
from langgraph.graph import StateGraph, START, END
from src.models import State
from src.nodes.worker import worker
from src.nodes.reducer import reducer


def build_graph():
    graph = StateGraph(State)
    graph.add_node("orchestrator", orchestrator)
    graph.add_node("worker", worker)
    graph.add_node("reducer", reducer)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "worker")
    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", END)

    return graph.compile()
