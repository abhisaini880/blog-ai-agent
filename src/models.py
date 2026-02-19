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
    needs_research: bool = Field(
        description="Whether this section requires web research for current data, tools, or benchmarks"
    )
    needs_image: bool = Field(
        description="Whether this section would benefit from a mermaid diagram or excalidraw image"
    )


class Plan(BaseModel):
    blog_title: str
    tasks: list[Task]


class ResearchResult(BaseModel):
    section_title: str
    sources: list[str]
    key_findings: list[str]


class DiagramSpec(BaseModel):
    mermaid_code: str = Field(description="Valid Mermaid diagram syntax")
    alt_text: str = Field(description="Descriptive alt text for the diagram")


class ImageResult(BaseModel):
    section_title: str
    image_path: str
    alt_text: str


class Section(BaseModel):
    title: str
    content: str


class State(TypedDict):
    topic: str
    plan: Plan
    feedback: str
    research: Annotated[List[ResearchResult], operator.add]
    sections: Annotated[List[Section], operator.add]
    final: str
    token_usage: Annotated[List[TokenUsage], operator.add]
    images: Annotated[List[ImageResult], operator.add]
