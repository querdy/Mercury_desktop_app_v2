from sqlalchemy import insert, select, delete
from sqlalchemy.orm import Session

from app.database import models
from app.schema.immunization import ImmunizationSchema


def delete_immunization_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    db.execute(
        delete(models.BaseImmunization)
        .where(models.BaseImmunization.enterprise_uuid == enterprise_uuid)
    )
    db.commit()


def get_base_immunization_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    base_research = db.scalars(
        select(models.BaseImmunization)
        .where(models.BaseImmunization.enterprise_uuid == enterprise_uuid)
    )
    return base_research.all()


def get_special_immunization_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    special_immunization = db.scalars(
        select(models.SpecialImmunization)
        .where(models.SpecialImmunization.enterprise_uuid == enterprise_uuid)
    )
    return special_immunization.all()


def get_special_immunization_for_product(db: Session, enterprise_uuid: str, product: str):
    special_research = db.scalars(
        select(models.SpecialImmunization)
        .where(models.SpecialImmunization.enterprise_uuid == enterprise_uuid)
        .where(models.SpecialImmunization.product == product)
    )
    return special_research.all()


def update_immunization(db: Session, enterprise_uuid: str, immunization: list[ImmunizationSchema]):
    db.execute(
        delete(models.BaseImmunization)
        .where(models.BaseImmunization.enterprise_uuid == enterprise_uuid)
    )
    if immunization:
        immunization_dict = [item.model_dump() for item in immunization]
        for item in immunization_dict:
            item['enterprise_uuid'] = enterprise_uuid

        db.execute(
            insert(models.BaseImmunization)
            .values(immunization_dict)
        )

    db.commit()

    return get_base_immunization_by_enterprise_uuid(db, enterprise_uuid)


def update_special_immunization(db: Session, enterprise_uuid: str, immunization: list[ImmunizationSchema]):
    db.execute(
        delete(models.SpecialImmunization)
        .where(models.SpecialImmunization.enterprise_uuid == enterprise_uuid)
    )
    if immunization:
        immunization_dict = [item.model_dump() for item in immunization]
        for item in immunization_dict:
            item['enterprise_uuid'] = enterprise_uuid

        db.execute(
            insert(models.SpecialImmunization)
            .values(immunization_dict)
        )

    db.commit()

    return get_special_immunization_by_enterprise_uuid(db, enterprise_uuid)
