
from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    status: str = "todo"


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    status: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    board_id: int

    model_config = ConfigDict(from_attributes=True)
