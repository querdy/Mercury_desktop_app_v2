from typing import Optional

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class VetisUserCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: str
    password: str


class VetisUserSchema(VetisUserCreateSchema):
    uuid: Optional[UUID]
