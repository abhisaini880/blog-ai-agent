from src.llm import get_llm
from src.models import Plan, State
from langchain_core.messages import SystemMessage, HumanMessage


def orchestrator(state: State) -> dict:
    llm = get_llm()
    feedback = state.get("feedback")
    topic = state["topic"]

    if feedback:
        previous_plan = state.get("plan")
        prompt = f"""
            The previous blog plan was rejected with the following feedback: {feedback}
            Please create a revised blog post plan for the topic: {topic} that addresses this feedback.
            Previous plan:
            Title: {previous_plan.blog_title}
            Sections:
            {'\n'.join([f"- {t.title}: {t.brief}" for t in previous_plan.tasks])}
        """
    else:
        prompt = f"Create a blog post plan for the topic: {topic}"

    plan = llm.with_structured_output(Plan).invoke(
        [
            SystemMessage(
                content="""
                    You are an expert technical blog post planner.
                    Given a topic, create a structured plan with 5-7 sections.
                    Rules:
                    - First section should be an engaging introduction (not titled "Introduction")
                    - Last section should be a practical takeaway or conclusion
                    - Each section brief should describe the KEY POINT to convey, not just the topic
                    - Briefs should be 1-2 sentences max
                    - The blog title should be compelling and specific, not generic
                """
            ),
            HumanMessage(content=prompt),
        ]
    )
    return {"plan": plan, "feedback": ""}
