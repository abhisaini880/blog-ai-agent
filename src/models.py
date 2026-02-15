from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated
import operator


class Task(BaseModel):
    id: int
    title: str
    brief: str = Field(..., description="A short description of the task")


class Plan(BaseModel):
    blog_title: str
    tasks: list[Task]


class State(TypedDict):
    topic: str
    plan: Plan
    sections: Annotated[List[str], operator.add]
    final: str
