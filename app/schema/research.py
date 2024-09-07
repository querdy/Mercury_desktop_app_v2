from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


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


class ResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    product: Optional[str] = None
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

    @field_validator('sampling_number', 'method')
    def validate_string_length(cls, value):
        value = value.strip()
        if len(value) > 255:
            raise ValueError('Длина строки не должна превышать 255 символов')
        return value

    @field_validator('operator', 'disease', 'expertise_id', 'conclusion')
    def validate_not_null_string_length(cls, value):
        value = value.strip()
        if len(value) > 255 or len(value) < 1:
            raise ValueError('Длина должна быть от 1 до 255 символов')
        return value

    @field_validator('product')
    def validate_products(cls, value):
        if value is None:
            return value
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
