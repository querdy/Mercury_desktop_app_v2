from typing import Generic, Type, Optional, Sequence, TypeVar

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.database.postgres import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get(self, uuid: str) -> Optional[ModelType]:
        result = self.session.scalar(
            select(self.model)
            .where(self.model.uuid == uuid)
        )
        return result

    def get_all(self) -> Sequence[ModelType]:
        result = self.session.scalars(
            select(self.model)
        )
        return result.all()

    def delete(self, uuid: str) -> None:
        self.session.execute(
            delete(self.model)
            .where(self.model.uuid == uuid)
        )

    def delete_by_enterprise_uuid(self, uuid: str) -> None:
        self.session.execute(
            delete(self.model)
            .where(self.model.enterprise_uuid == uuid)
        )
