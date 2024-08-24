from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4

from app.database.postgre import Base


class Enterprise(Base):
    __tablename__ = "enterprise"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    name: Mapped[str] = mapped_column(unique=True)
    pk: Mapped[str]
    base_research = relationship("BaseResearch", back_populates="enterprise")
    special_research = relationship("SpecialResearch", back_populates="enterprise")
    exclude_product = relationship("ExcludeProducts", back_populates="enterprise")
    base_immunization = relationship("BaseImmunization", back_populates="enterprise")
    special_immunization = relationship("SpecialImmunization", back_populates="enterprise")
    