from sqlalchemy import insert, select, delete
from sqlalchemy.orm import Session

from app.database.models import VetisUser
from app.database.repositories.base import BaseRepository
from app.schema.vetis_user import VetisUserCreateSchema, VetisUserSchema


class UserRepository(BaseRepository[VetisUser]):
    def __init__(self, session: Session):
        super().__init__(session, VetisUser)

    def create(self, entity: VetisUserCreateSchema):
        self.session.execute(
            delete(self.model)
        )
        result = self.session.scalar(
            insert(self.model)
            .values(entity.model_dump())
            .returning(self.model)
        )
        return result

    def receive(self):
        user = self.session.scalar(
            select(self.model)
        )
        if user is not None:
            return VetisUserSchema.from_orm(user)
