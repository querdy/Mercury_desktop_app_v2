from typing import Optional

from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.schema.immunization import ImmunizationSchema, SpecialImmunizationSchema
from app.schema.research import ResearchSchema, SpecialResearchSchema


class EnterpriseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: Optional[UUID] = None
    name: str
    pk: str
    base_research: Optional[list[ResearchSchema]] = None
    product_exclude_from_base: Optional[list[str]] = None
    special_research: Optional[list[SpecialResearchSchema]] = None
    base_immunization: Optional[list[ImmunizationSchema]] = None
    special_immunization: Optional[list[SpecialImmunizationSchema]] = None
