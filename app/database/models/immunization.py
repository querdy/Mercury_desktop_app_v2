from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base


class Immunization(Base):
    __tablename__ = "immunization"

    product: Mapped[str] = mapped_column(nullable=True)
    operation_type: Mapped[str]
    illness: Mapped[str]
    operation_date: Mapped[str]
    vaccine_name: Mapped[str] = mapped_column(nullable=True)
    vaccine_serial: Mapped[str] = mapped_column(nullable=True)
    vaccine_date_to: Mapped[str] = mapped_column(nullable=True)
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise.uuid", ondelete="CASCADE"))
    enterprise = relationship("Enterprise", back_populates="immunization", uselist=False)
