from typing import Sequence

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

from app.database.models import Immunization
from app.database.repositories.base import BaseRepository
from app.schema.immunization import ImmunizationSchema


class ImmunizationRepository(BaseRepository[Immunization]):
    def __init__(self, session: Session):
        super().__init__(session, Immunization)

    def update(self, enterprise_uuid: str, items: Sequence[ImmunizationSchema]):
        self.session.execute(
            delete(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
        )
        if items:
            items_dict = [item.model_dump() for item in items]
            for item in items_dict:
                item['enterprise_uuid'] = enterprise_uuid

            result = self.session.execute(
                insert(self.model)
                .values(items_dict)
                .returning(self.model)
            ).all()
            return [ImmunizationSchema.from_orm(item[0]) for item in result]
        return []

    def get_base_by_enterprise_uuid(self, enterprise_uuid: str) -> Sequence[ImmunizationSchema]:
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
            .where(self.model.product.is_(None))
        ).all()
        return [ImmunizationSchema.from_orm(item) for item in result]

    def get_special_by_enterprise_uuid(self, enterprise_uuid: str) -> Sequence[ImmunizationSchema]:
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
            .where(self.model.product.isnot(None))
        ).all()
        return [ImmunizationSchema.from_orm(item) for item in result]

    def get_special_for_product_by_enterprise_uuid(self, enterprise_uuid: str, product: str) -> Sequence[ImmunizationSchema]:
        result = self.session.scalars(
            select(self.model)
            .where(self.model.enterprise_uuid == enterprise_uuid)
            .where(self.model.product == product)
        ).all()
        return [ImmunizationSchema.from_orm(item) for item in result]
