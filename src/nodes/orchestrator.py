from src.llm import LLM
from src.models import Plan, State
from langchain_core.messages import SystemMessage, HumanMessage


def orchestrator(state: State) -> dict:
    llm = LLM(node_name="orchestrator")
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

    plan = llm.invoke_structured(
        [
            SystemMessage(
                content="""You are a senior technical writer who publishes on Medium.
                    Given a topic, create a blog plan with 5-7 sections.

                    Structure rules:
                    - Open with a hook: a bold claim, a question, or a relatable problem
                    - DO NOT title the first section "Introduction" — use something specific
                    - Each middle section should make ONE clear point with a concrete example
                    - End with actionable takeaways, not a generic "Conclusion"
                    - The blog title should be specific and curiosity-driven
                    Good: "Why Your Microservices Are Failing (And It's Not the Architecture)"
                    Bad: "An Overview of Microservices Architecture"

                    Section briefs should describe the KEY ARGUMENT, not just the topic.
                    Good: "Explain why event sourcing solves the dual-write problem with a payment system example"
                    Bad: "Discuss event sourcing"

                    For each section, decide:
                    - needs_research: True if it requires current data, specific tools/versions, 
                    benchmarks, or recent developments. False for conceptual explanations, 
                    analogies, or opinion-based sections.
                    - needs_image: True if the section describes an architecture, workflow, 
                    data flow, or comparison that benefits from a visual. False for 
                    narrative sections, introductions, or conclusions.
                """
            ),
            HumanMessage(content=prompt),
        ],
        Plan,
    )
    return {"plan": plan, "feedback": "", "token_usage": llm.usage}
