from typing import Optional

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class EnterpriseCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    pk: str


class EnterpriseShortSchema(EnterpriseCreateSchema):
    uuid: Optional[UUID] = None
