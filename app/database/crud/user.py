from sqlalchemy import insert, select, delete
from sqlalchemy.orm import Session

from app.database import models
from app.schema.user import VetisUserSchema


def create_user(db: Session, user: VetisUserSchema):
    db.execute(
        delete(models.VetisUser)
    )
    user = db.scalar(
        insert(models.VetisUser)
        .values(
            login=user.login,
            password=user.password
        )
        .returning(models.VetisUser)
    )
    db.commit()
    return user


def get_user(db: Session):
    user = db.scalar(
        select(models.VetisUser)
    )
    return user
