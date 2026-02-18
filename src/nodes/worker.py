from src.models import State
from src.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage


def worker(payload: dict) -> dict:
    llm = get_llm()
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
                content="""
                    You are an expert technical blog writer.
                    Write a section for a blog post in markdown format.

                    Rules:
                    - Write 150-250 words for this section
                    - Use a conversational but authoritative tone
                    - Include concrete examples where relevant
                    - Use subheadings (##) only if the section needs subdivision
                    - Do NOT use filler phrases like "In today's world" or "It's important to note"
                    - Incorporate the provided research sources with inline citations as [Source Title](URL)
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

    return {"sections": [section]}
