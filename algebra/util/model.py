from pydantic import BaseModel, ConfigDict


class AlgebraModelBase(BaseModel):
    model_config = ConfigDict(frozen=True)
