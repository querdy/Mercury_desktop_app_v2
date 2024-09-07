from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base


class Research(Base):
    __tablename__ = "research"

    product: Mapped[str] = mapped_column(nullable=True)
    sampling_number: Mapped[str] = mapped_column(nullable=True)
    sampling_date: Mapped[str] = mapped_column(nullable=True)
    operator: Mapped[str]
    disease: Mapped[str]
    date_of_research: Mapped[str]
    method: Mapped[str] = mapped_column(nullable=True)
    expertise_id: Mapped[str]
    result: Mapped[str]
    conclusion: Mapped[str]
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise.uuid", ondelete="CASCADE"))
    enterprise = relationship("Enterprise", back_populates="research", uselist=False)


class ExcludeProducts(Base):
    __tablename__ = "exclude_products"

    product: Mapped[str]
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise.uuid", ondelete="CASCADE"))
    enterprise = relationship("Enterprise", back_populates="exclude_product", uselist=False)
