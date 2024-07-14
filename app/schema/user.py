from pydantic import BaseModel, ConfigDict, field_validator


class VetisUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: str
    password: str

    @field_validator('login')
    def _login(cls, value):
        value = value.strip()
        return value

    @field_validator('password')
    def _password(cls, value):
        value = value.strip()
        return value
