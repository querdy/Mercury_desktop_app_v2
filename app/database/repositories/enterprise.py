from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from app.database.models import Enterprise
from app.database.repositories.base import BaseRepository
from app.schema.enterprise import EnterpriseShortSchema, EnterpriseCreateSchema


class EnterpriseRepository(BaseRepository[Enterprise]):
    def __init__(self, session: Session):
        super().__init__(session, Enterprise)

    def create(self, entity: EnterpriseCreateSchema):
        result = self.session.scalar(
            insert(self.model)
            .values(entity.model_dump(exclude_none=True))
            .returning(self.model)
        )
        return result

    def get_by_name(self, name: str) -> Optional[Enterprise]:
        result = self.session.scalar(
            select(self.model)
            .where(self.model.name == name)
        )
        return result

    def get_all(self) -> list[EnterpriseShortSchema]:
        result = self.session.scalars(
            select(self.model)
            .order_by(self.model.name)
        ).all()
        return [EnterpriseShortSchema.from_orm(item) for item in result]

    def get(self, uuid: str) -> Optional[EnterpriseShortSchema]:
        result = self.session.scalar(
            select(self.model)
            .where(self.model.uuid == uuid)
        )
        return EnterpriseShortSchema.from_orm(result)
