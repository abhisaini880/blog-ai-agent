from src.llm import LLM
from langchain_core.messages import SystemMessage, HumanMessage
from src.models import Section


def worker(payload: dict) -> dict:
    llm = LLM(node_name="worker")
    task = payload["task"]
    plan = payload["plan"]
    topic = payload["topic"]
    research = payload.get("research")

    research_context = ""
    if research:
        findings = "\n".join(f"- {f}" for f in research.key_findings)
        sources = "\n".join(f"- [{s}]({s})" for s in research.sources)
        research_context = (
            f"\n\nResearch findings:\n{findings}\n\nSources (cite inline):\n{sources}"
        )

    section = llm.invoke(
        [
            SystemMessage(
                content="""You are a senior engineer who writes popular Medium blog posts.
                    Write a section for a technical blog post.

                    Writing style:
                    - Short paragraphs (2-3 sentences max)
                    - Start the section with a bold statement or insight, not a definition
                    - Use "you" to address the reader directly
                    - Use **bold** for key terms on first mention
                    - Include at least one concrete example, code snippet, or analogy
                    - Use transitional phrases between paragraphs
                    - Avoid: "In today's world", "It's worth noting", "In conclusion",
                    "Let's dive in", "As we all know", "In this section"
                    - Write like you're explaining to a smart colleague over coffee

                    Length: 300 words for this section.

                    If research sources are provided, cite them naturally inline as
                    [Source Title](URL) — don't dump all links at the end.
                """
            ),
            HumanMessage(
                content=f"""
                    Write the section for the task: {task.title} ({task.brief}) 
                    in the blog post titled '{plan.blog_title}' about the topic: {topic}.
                    {research_context} Return only the markdown content of the section.
                """
            ),
        ]
    ).content.strip()

    return {
        "sections": [Section(title=task.title, content=section)],
        "token_usage": llm.usage,
    }
