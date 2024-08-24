from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID


class ImmunizationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    operation_type: str
    illness: str
    operation_date: str
    vaccine_name: Optional[str] = ""
    vaccine_serial: Optional[str] = ""
    vaccine_date_to: Optional[str] = ""

    def __eq__(self, other):
        return (
            self.operation_type == other.operation_type and
            self.illness == other.illness and
            self.operation_date == other.operation_date and
            self.vaccine_name == other.vaccine_name and
            self.vaccine_serial == other.vaccine_serial and
            self.vaccine_date_to == other.vaccine_date_to
        )

    @field_validator('operation_type', 'illness', 'vaccine_name', 'vaccine_serial')
    def validate_string_length(cls, value):
        value = value.strip()
        if len(value) > 255:
            raise ValueError('Длина строки не должна превышать 255 символов')
        return value

    @field_validator('operation_date', 'vaccine_date_to')
    def validate_date_format(cls, value):
        if value:
            value = value.strip()
            try:
                datetime.strptime(value, "%d.%m.%Y")
            except ValueError:
                raise ValueError('Формат даты должен соответствовать %d.%m.%Y')
        return value

    @field_validator('operation_type')
    def validate_operation_type(cls, value):
        value = value.strip()
        if value not in {'0', '1'}:
            raise ValueError('operation_type должно быть 0 или 1')
        return value


class SpecialImmunizationSchema(ImmunizationSchema):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    product: str

    def __eq__(self, other):
        return (
            self.product == other.product and
            self.operation_type == other.operation_type and
            self.illness == other.illness and
            self.operation_date == other.operation_date and
            self.vaccine_name == other.vaccine_name and
            self.vaccine_serial == other.vaccine_serial and
            self.vaccine_date_to == other.vaccine_date_to
        )

    @field_validator('product')
    def validate_string_length(cls, value):
        value = value.strip()
        if len(value) > 255:
            raise ValueError('Длина строки не должна превышать 255 символов')
        return value


class EnterpriseForImmunizationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: Optional[UUID] = None
    name: str
    base: Optional[list[ImmunizationSchema]] = None
    special: Optional[list[SpecialImmunizationSchema]] = None
