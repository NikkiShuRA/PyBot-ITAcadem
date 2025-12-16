from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    class Config:
        model_config = ConfigDict(from_attributes=True, extra="forbid")
