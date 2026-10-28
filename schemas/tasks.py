from pydantic import BaseModel

class TaskCreate(BaseModel):
    name: str
    description: str | None
    status: str

class TaskUpdate(BaseModel):
    new_status: str