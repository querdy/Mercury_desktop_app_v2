from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, ConfigDict


class ResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

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

    @field_validator('sampling_number', 'operator', 'disease', 'method', 'expertise_id', 'conclusion')
    def validate_string_length(cls, value):
        value = value.strip()
        if len(value) > 255:
            raise ValueError('Длина строки не должна превышать 255 символов')
        return value

    @field_validator('date_of_research', 'sampling_date')
    def validate_date_format(cls, value):
        if value:
            value = value.strip()
            try:
                datetime.strptime(value, "%d.%m.%Y")
            except ValueError:
                raise ValueError('Формат даты должен соответствовать %d.%m.%Y')
        return value

    @field_validator('result')
    def validate_result(cls, value):
        value = value.strip()
        if value not in {'1', '2', '3'}:
            raise ValueError('result должно быть 1, 2 или 3')
        return value


class SpecialResearchSchema(ResearchSchema):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    product: str

    @field_validator('product')
    def validate_string_length(cls, value):
        value = value.strip()
        if len(value) > 255:
            raise ValueError('Длина строки не должна превышать 255 символов')
        return value


class ExcludeProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    product: str

    @field_validator('product')
    def _product(cls, value):
        return value.strip()

    def __eq__(self, other):
        return (
            self.product == other.product
        )
