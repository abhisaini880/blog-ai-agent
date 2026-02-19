from src.config import config
from langchain_openai import ChatOpenAI
from typing import Any
from src.models import TokenUsage


class LLM:
    def __init__(self, node_name: str = "unknown"):
        self._llm = ChatOpenAI(
            model=config.MODEL_NAME,
            base_url=config.BASE_URL,
            api_key=config.API_KEY,
        )
        self._node_name = node_name
        self._usage: list[TokenUsage] = []

    def invoke(self, messages):
        response = self._llm.invoke(messages)
        self._track(response.usage_metadata)
        return response

    def invoke_structured(self, messages, schema):
        response = self._llm.with_structured_output(schema, include_raw=True).invoke(
            messages
        )
        self._track(response["raw"].usage_metadata)
        return response["parsed"]

    def with_tools(self, tools):
        clone = LLM.__new__(LLM)
        clone._llm = self._llm.bind_tools(tools)
        clone._node_name = self._node_name
        clone._usage = self._usage
        return clone

    def _track(self, metadata):
        if metadata:
            self._usage.append(
                TokenUsage(
                    node=self._node_name,
                    input_tokens=metadata.get("input_tokens", 0),
                    output_tokens=metadata.get("output_tokens", 0),
                    total_tokens=metadata.get("total_tokens", 0),
                )
            )

    @property
    def usage(self) -> list[TokenUsage]:
        return self._usage
