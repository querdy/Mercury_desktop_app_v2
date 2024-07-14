from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from app.database.postgre import Base


class VetisUser(Base):
    __tablename__ = "vetis_user"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
