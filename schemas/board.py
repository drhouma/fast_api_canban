from pydantic import BaseModel, ConfigDict, Field


class BoardCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    is_personal: bool = True


class BoardUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )


class BoardResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_personal: bool

    model_config = ConfigDict(from_attributes=True)
