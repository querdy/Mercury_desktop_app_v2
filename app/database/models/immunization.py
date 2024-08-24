from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4

from app.database.postgre import Base


class BaseImmunization(Base):
    __tablename__ = "base_immunization"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    operation_type: Mapped[str]
    illness: Mapped[str]
    operation_date: Mapped[str]
    vaccine_name: Mapped[str] = mapped_column(nullable=True)
    vaccine_serial: Mapped[str] = mapped_column(nullable=True)
    vaccine_date_to: Mapped[str] = mapped_column(nullable=True)
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise.uuid", ondelete="CASCADE"))
    enterprise = relationship("Enterprise", back_populates="base_immunization", uselist=False)


class SpecialImmunization(Base):
    __tablename__ = "special_immunization"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    product: Mapped[str]
    operation_type: Mapped[str]
    illness: Mapped[str]
    operation_date: Mapped[str]
    vaccine_name: Mapped[str] = mapped_column(nullable=True)
    vaccine_serial: Mapped[str] = mapped_column(nullable=True)
    vaccine_date_to: Mapped[str] = mapped_column(nullable=True)
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise.uuid", ondelete="CASCADE"))
    enterprise = relationship("Enterprise", back_populates="special_immunization", uselist=False)