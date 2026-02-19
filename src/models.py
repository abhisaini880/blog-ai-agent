from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated
import operator


class TokenUsage(BaseModel):
    node: str
    input_tokens: int
    output_tokens: int
    total_tokens: int


class Task(BaseModel):
    id: int
    title: str
    brief: str = Field(..., description="A short description of the task")


class Plan(BaseModel):
    blog_title: str
    tasks: list[Task]


class ResearchResult(BaseModel):
    section_title: str
    sources: list[str]
    key_findings: list[str]


class State(TypedDict):
    topic: str
    plan: Plan
    feedback: str
    research: Annotated[List[ResearchResult], operator.add]
    sections: Annotated[List[str], operator.add]
    final: str
    token_usage: Annotated[List[TokenUsage], operator.add]
