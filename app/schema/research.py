from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, ConfigDict


class ResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sampling_number: Optional[str] = ""
    sampling_date: Optional[str] = ""
    operator: str
    method: str
    disease: str
    date_of_research: str
    expertise_id: str
    result: str
    conclusion: str

    def __eq__(self, other):
        return (
            self.sampling_number == other.sampling_number and
            self.sampling_date == other.sampling_date and
            self.operator == other.operator and
            self.method == other.method and
            self.disease == other.disease and
            self.date_of_research == other.date_of_research and
            self.expertise_id == other.expertise_id and
            self.result == other.result and
            self.conclusion == other.conclusion
        )

    @field_validator('sampling_number')
    def _sampling_number(cls, value):
        value = value.strip()
        if len(value) <= 255:
            return value
        raise ValueError('Длина строки не должна превышать 255 символов')

    @field_validator('date_of_research')
    def _date_of_research(cls, value):
        value = value.strip()
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return value
        except ValueError:
            raise ValueError('Формат даты должен соответствовать %d.%m.%Y')

    @field_validator('sampling_date')
    def _sampling_date(cls, value):
        if len(value) == 0:
            return value
        value = value.strip()
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return value
        except ValueError:
            raise ValueError('Формат даты должен соответствовать %d.%m.%Y')

    @field_validator('operator')
    def _operator(cls, value):
        value = value.strip()
        if len(value) <= 255:
            return value
        raise ValueError('Длина строки не должна превышать 255 символов')

    @field_validator('disease')
    def _disease(cls, value):
        value = value.strip()
        if len(value) <= 255:
            return value
        raise ValueError('Длина строки не должна превышать 255 символов')

    @field_validator('method')
    def _method(cls, value):
        value = value.strip()
        if len(value) <= 255:
            return value
        raise ValueError('Длина строки не должна превышать 255 символов')

    @field_validator('expertise_id')
    def _expertise_id(cls, value):
        value = value.strip()
        if len(value) <= 255:
            return value
        raise ValueError('Длина строки не должна превышать 255 символов')

    @field_validator('result')
    def _result(cls, value):
        value = value.strip()
        if value in {'1', '2', '3'}:
            return value
        raise ValueError('result должно быть 1, 2 или 3')

    @field_validator('conclusion')
    def _conclusion(cls, value):
        value = value.strip()
        if len(value) <= 255:
            return value
        raise ValueError('Длина строки не должна превышать 255 символов')


class SpecialResearchSchema(ResearchSchema):
    product: str

    @field_validator('product')
    def _product(cls, value):
        return value.strip()


class ExcludeProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: str

    @field_validator('product')
    def _product(cls, value):
        return value.strip()


class EnterpriseForResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: Optional[UUID] = None
    name: str
    base_research: Optional[list[ResearchSchema]] = None
    product_exclude_from_base: Optional[list[str]] = None
    special_research: Optional[list[SpecialResearchSchema]] = None
