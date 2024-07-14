from sqlalchemy import insert, select, delete, update
from sqlalchemy.orm import Session

from app.database import models
from app.database.models import BaseResearch
from app.schema.research import EnterpriseForResearchSchema, ResearchSchema, ExcludeProductSchema


def create_enterprise(db: Session, enterprise: EnterpriseForResearchSchema):
    enterprise = db.scalar(
        insert(models.EnterpriseForResearch)
        .values(
            name=enterprise.name
        )
        .returning(models.EnterpriseForResearch)
    )
    db.commit()
    return enterprise


def get_all_enterprise(db: Session):
    enterprises = db.scalars(
        select(models.EnterpriseForResearch)
        .order_by(models.EnterpriseForResearch.name)
    )
    return enterprises.all()


def get_enterprise_by_uuid(db: Session, enterprise_uuid: str):
    enterprise = db.scalar(
        select(models.EnterpriseForResearch)
        .where(models.EnterpriseForResearch.uuid == enterprise_uuid)
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
            delete(models.EnterpriseForResearch)
            .where(models.EnterpriseForResearch.uuid == enterprise_uuid)
        )
        db.commit()
    except Exception as e:
        print(f"{type(e)} {e}")


def delete_research_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    db.execute(
        delete(models.BaseResearch)
        .where(models.BaseResearch.enterprise_uuid == enterprise_uuid)
    )
    db.commit()


def get_base_research_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    base_research = db.scalars(
        select(models.BaseResearch)
        .where(models.BaseResearch.enterprise_uuid == enterprise_uuid)
    )
    return base_research.all()


def get_special_research_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    special_research = db.scalars(
        select(models.SpecialResearch)
        .where(models.SpecialResearch.enterprise_uuid == enterprise_uuid)
    )
    return special_research.all()


def get_special_research_for_product(db: Session, enterprise_uuid: str, product: str):
    special_research = db.scalars(
        select(models.SpecialResearch)
        .where(models.SpecialResearch.enterprise_uuid == enterprise_uuid)
        .where(models.SpecialResearch.product == product)
    )
    return special_research.all()


def get_exclude_products_by_enterprise_uuid(db: Session, enterprise_uuid: str):
    exclude_products = db.scalars(
        select(models.ExcludeProducts)
        .where(models.ExcludeProducts.enterprise_uuid == enterprise_uuid)
    )
    return exclude_products.all()


def update_research(db: Session, enterprise_uuid: str, base_research: list[ResearchSchema]):
    db.execute(
        delete(models.BaseResearch)
        .where(models.BaseResearch.enterprise_uuid == enterprise_uuid)
    )

    researches_dict = [item.model_dump() for item in base_research]
    for item in researches_dict:
        item['enterprise_uuid'] = enterprise_uuid

    db.execute(
        insert(models.BaseResearch)
        .values(researches_dict)
    )

    db.commit()

    return get_base_research_by_enterprise_uuid(db, enterprise_uuid)


def update_special_research(db: Session, enterprise_uuid: str, special_research: list[ResearchSchema]):
    db.execute(
        delete(models.SpecialResearch)
        .where(models.SpecialResearch.enterprise_uuid == enterprise_uuid)
    )

    researches_dict = [item.model_dump() for item in special_research]
    for item in researches_dict:
        item['enterprise_uuid'] = enterprise_uuid

    db.execute(
        insert(models.SpecialResearch)
        .values(researches_dict)
    )

    db.commit()

    return get_special_research_by_enterprise_uuid(db, enterprise_uuid)


def update_exclude_products(db: Session, products: list[ExcludeProductSchema], enterprise_uuid: str):
    db.execute(
        delete(models.ExcludeProducts)
        .where(models.ExcludeProducts.enterprise_uuid == enterprise_uuid)
    )

    products_dict = [item.dict() for item in products]
    for item in products_dict:
        item['enterprise_uuid'] = enterprise_uuid

    db.execute(
        insert(models.ExcludeProducts).values(products_dict)
    )

    db.commit()

    return get_exclude_products_by_enterprise_uuid(db, enterprise_uuid)
