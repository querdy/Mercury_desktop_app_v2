from typing import Sequence

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.database.models import Research
from app.database.repositories.base import BaseRepository
from app.schema.research import ResearchSchema


class ResearchRepository(BaseRepository[Research]):
    def __init__(self, session: Session):
        super().__init__(session, Research)

    def update(self, enterprise_uuid: str, items: Sequence[ResearchSchema]):
        self.session.execute(
            delete(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
        )
        if items:
            researches_dict = [item.model_dump() for item in items]
            for item in researches_dict:
                item['enterprise_uuid'] = enterprise_uuid

            result = self.session.execute(
                insert(self.model)
                .values(researches_dict)
                .returning(self.model)
            ).all()
            return [ResearchSchema.from_orm(item[0]) for item in result]
        return []

    def get_base_by_enterprise_uuid(self, enterprise_uuid: str) -> Sequence[ResearchSchema]:
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
            .where(self.model.product.is_(None))
        ).all()
        return [ResearchSchema.from_orm(item) for item in result]

    def get_special_by_enterprise_uuid(self, enterprise_uuid: str) -> Sequence[ResearchSchema]:
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
            .where(self.model.product.isnot(None))
        ).all()
        return [ResearchSchema.from_orm(item) for item in result]

    def get_special_for_product_by_enterprise_uuid(self, enterprise_uuid: str, product: str) -> Sequence[ResearchSchema]:
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
            .where(self.model.product == product)
        ).all()
        return [ResearchSchema.from_orm(item) for item in result]