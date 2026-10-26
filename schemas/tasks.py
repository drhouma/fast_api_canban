from pydantic import BaseModel

class TaskCreate(BaseModel):
    name: str
    description: str | None
    status: str