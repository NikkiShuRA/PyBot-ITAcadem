from pydantic import BaseModel, ConfigDict


class BaseEntityModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
