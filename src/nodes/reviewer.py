from langgraph.types import Command, interrupt
from src.models import State


def plan_review(state: State) -> Command:
    plan = state["plan"]

    decision = interrupt(
        {
            "question": "Review the blog plan:",
            "plan": f"Title: {plan.blog_title}\n\nSections:\n"
            + "\n".join([f"- {t.title}: {t.brief}" for t in plan.tasks]),
        }
    )

    if decision["action"] == "approve":
        return Command(goto="pre_research")
    else:
        return Command(goto="orchestrator", update={"feedback": decision["feedback"]})
