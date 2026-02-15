from src.llm import get_llm
from src.models import Plan, State
from langchain_core.messages import SystemMessage, HumanMessage

llm = get_llm()


def orchestrator(state: State) -> dict:
    plan = llm.with_structured_output(Plan).invoke(
        [
            SystemMessage(
                content="You are an expert blog post planner. Given a blog topic, you will create a clean plan for the blog post with 5-7 sections."
            ),
            HumanMessage(
                content=f"Create a blog post plan for the topic: {state['topic']}"
            ),
        ]
    )
    return {"plan": plan}
