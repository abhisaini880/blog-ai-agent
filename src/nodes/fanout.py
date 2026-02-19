from langgraph.types import Send
from src.models import State
from typing import List


def fanout_to_researchers(state: State) -> List[Send]:
    tasks = state["plan"].tasks
    send_objs = []
    for task in tasks:
        if task.needs_research:
            obj = Send(
                node="researcher",
                arg={
                    "topic": state["topic"],
                    "task": task,
                },
            )
            send_objs.append(obj)
    return send_objs


def fanout_to_writers(state: State) -> List[Send]:
    research_map = {r.section_title: r for r in state["research"]}
    tasks = state["plan"].tasks
    send_objs = []
    for task in tasks:
        obj = Send(
            node="worker",
            arg={
                "plan": state["plan"],
                "topic": state["topic"],
                "task": task,
                "research": research_map.get(task.title),
            },
        )
        send_objs.append(obj)
    return send_objs
