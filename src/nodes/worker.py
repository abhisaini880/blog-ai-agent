from src.models import State
from src.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

llm = get_llm()


def worker(state: State) -> dict:
    tasks = state["plan"].tasks
    blog_title = state["plan"].blog_title
    topic = state["topic"]
    sections = []
    for task in tasks:
        section = llm.invoke(
            [
                SystemMessage(
                    content="You are an expert blog post writer. Given a blog topic and a task from the blog post plan, you will write a clean section for the blog post in markdown format."
                ),
                HumanMessage(
                    content=f"Write the section for the task: {task.title} ({task.brief}) in the blog post titled '{blog_title}' about the topic: {topic}. Return only the markdown content of the section."
                ),
            ]
        ).content.strip()
        sections.append(section)
    return {"sections": sections}
