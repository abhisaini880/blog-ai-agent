from src.llm import LLM
from src.models import ResearchResult
from src.tools.search import web_search
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage


def researcher(payload: dict) -> dict:
    task = payload["task"]
    topic = payload["topic"]

    llm = LLM(node_name="researcher")
    llm_with_tools = llm.with_tools([web_search])

    messages = [
        SystemMessage(
            content="""You are a research assistant gathering information for a blog section.
                You have access to a web_search tool for finding current information.
                
                - If the topic requires recent data, statistics, or specific technical details, 
                use web_search to find 2-3 high-quality sources.
                - If the topic is well-established and you're confident in your knowledge, 
                you may respond directly without searching.
                - Always prefer searching when the topic involves specific tools, versions, 
                benchmarks, or recent developments."""
        ),
        HumanMessage(
            content=f"Research the topic '{task.title}' ({task.brief}) for a technical blog about '{topic}'. "
            f"Search for recent, authoritative sources."
        ),
    ]

    response = llm_with_tools.invoke(messages)

    while response.tool_calls:
        messages.append(response)

        for tc in response.tool_calls:
            result = web_search.invoke(tc["args"])
            messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

        response = llm_with_tools.invoke(messages)

    raw_research = response.content

    research_result = llm.invoke_structured(
        [
            SystemMessage(
                content="Extract the research findings into a structured format. "
                "Include all source URLs found and the key findings."
            ),
            HumanMessage(
                content=f"Section title: {task.title}\n\nRaw research:\n{raw_research}"
            ),
        ],
        ResearchResult,
    )

    return {"research": [research_result], "token_usage": llm.usage}
