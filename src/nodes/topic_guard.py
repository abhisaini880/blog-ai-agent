from src.llm import LLM
from src.models import TopicCheck, State
from langchain_core.messages import SystemMessage, HumanMessage


def topic_guard(state: State) -> dict:
    llm = LLM(node_name="topic_guard")

    result = llm.invoke_structured(
        [
            SystemMessage(
                content="""You decide whether a topic is suitable for a technical engineering blog.

                Accept topics about: software engineering, system design, architecture,
                DevOps, cloud, databases, networking, security, ML/AI, data engineering,
                programming languages, frameworks, APIs, protocols, or any other
                technology / computer-science subject.

                Reject topics that are clearly non-technical: lifestyle, cooking, politics,
                sports, entertainment, travel, fashion, etc.

                When in doubt, accept — technical writers often find engineering angles
                in surprising places."""
            ),
            HumanMessage(content=f"Topic: {state['topic']}"),
        ],
        TopicCheck,
    )

    if result.is_technical:
        return {"topic_error": "", "token_usage": llm.usage}

    return {"topic_error": result.reason, "token_usage": llm.usage}
