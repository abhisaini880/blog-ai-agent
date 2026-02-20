from src.llm import LLM
from src.models import State
from langchain_core.messages import SystemMessage, HumanMessage


def rewriter(state: State) -> dict:
    llm = LLM(node_name="rewriter")

    improved = llm.invoke(
        [
            SystemMessage(
                content="""You are a senior technical editor. Rewrite the blog post
                to address the reviewer's feedback. Preserve the overall structure
                (title, section headings, images) and improve only the areas called out.

                Return the full improved blog in markdown."""
            ),
            HumanMessage(
                content=f"Blog:\n\n{state['final']}\n\n"
                f"Reviewer feedback:\n{state['eval_feedback']}"
            ),
        ]
    ).content.strip()

    return {"final": improved, "token_usage": llm.usage}
