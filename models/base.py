from pydantic import BaseModel, ConfigDict


class CreateModel(BaseModel):
    pass

class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UpdateModel(BaseModel):
    pass