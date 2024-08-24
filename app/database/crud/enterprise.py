from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

from app.database import models
from app.schema.enterprise import EnterpriseSchema


def create_enterprise(db: Session, enterprise: EnterpriseSchema):
    enterprise = db.scalar(
        insert(models.Enterprise)
        .values(
            name=enterprise.name,
            pk=enterprise.pk
        )
        .returning(models.Enterprise)
    )
    db.commit()
    return enterprise


def get_all_enterprise(db: Session):
    enterprises = db.scalars(
        select(models.Enterprise)
        .order_by(models.Enterprise.name)
    )
    return enterprises.all()


def get_enterprise_by_uuid(db: Session, enterprise_uuid: str):
    enterprise = db.scalar(
        select(models.Enterprise)
        .where(models.Enterprise.uuid == enterprise_uuid)
    )
    return enterprise


def delete_enterprise(db: Session, enterprise_uuid: str):
    try:
        db.execute(
            delete(models.BaseResearch)
            .where(models.BaseResearch.enterprise_uuid == enterprise_uuid)
        )
        db.execute(
            delete(models.SpecialResearch)
            .where(models.SpecialResearch.enterprise_uuid == enterprise_uuid)
        )
        db.execute(
            delete(models.ExcludeProducts)
            .where(models.ExcludeProducts.enterprise_uuid == enterprise_uuid)
        )
        db.execute(
            delete(models.BaseImmunization)
            .where(models.BaseImmunization.enterprise_uuid == enterprise_uuid)
        )
        db.execute(
            delete(models.SpecialImmunization)
            .where(models.SpecialImmunization.enterprise_uuid == enterprise_uuid)
        )
        db.execute(
            delete(models.Enterprise)
            .where(models.Enterprise.uuid == enterprise_uuid)
        )
        db.commit()
    except Exception as e:
        print(f"{type(e)} {e}")