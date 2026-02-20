from src.llm import LLM
from src.models import EvalResult, State
from langchain_core.messages import SystemMessage, HumanMessage


def evaluator(state: State) -> dict:
    llm = LLM(node_name="evaluator")

    result = llm.invoke_structured(
        [
            SystemMessage(
                content="""You are a senior technical editor. Evaluate this blog post
                on a 1-10 scale using these criteria:

                - Structure: clear flow, strong opening hook, actionable ending
                - Depth: concrete examples, code snippets, or real-world scenarios
                - Clarity: short paragraphs, direct tone, no filler phrases
                - Citations: research-backed claims have inline source links

                Score 7+ means publish-ready. Below 7, provide 2-3 specific,
                actionable improvements (not vague advice like "add more detail").

                If passed, feedback MUST be an empty string."""
            ),
            HumanMessage(content=f"Evaluate this blog post:\n\n{state['final']}"),
        ],
        EvalResult,
    )

    return {
        "eval_feedback": result.feedback if not result.passed else "",
        "eval_count": state.get("eval_count", 0) + 1,
        "token_usage": llm.usage,
    }
