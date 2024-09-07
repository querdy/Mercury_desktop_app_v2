from typing import Sequence

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from app.database.models import ExcludeProducts
from app.database.repositories.base import BaseRepository
from app.schema.research import ExcludeProductSchema


class ExcludeProductsRepository(BaseRepository[ExcludeProducts]):
    def __init__(self, session: Session):
        super().__init__(session, ExcludeProducts)

    def update(self, enterprise_uuid: str, items: Sequence[ExcludeProductSchema]):
        self.delete_by_enterprise_uuid(enterprise_uuid)
        if items:
            products_dict = [item.model_dump() for item in items]
            for item in products_dict:
                item['enterprise_uuid'] = enterprise_uuid

            result = self.session.execute(
                insert(self.model)
                .values(products_dict)
                .returning(self.model)
            ).all()
            return [ExcludeProductSchema.from_orm(item[0]) for item in result]
        return []

    def get_by_enterprise_uuid(self, enterprise_uuid: str):
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
        ).all()
        return [ExcludeProductSchema.from_orm(item) for item in result]
