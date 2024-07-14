from uuid import uuid4

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgre import Base


class EnterpriseForResearch(Base):
    __tablename__ = "enterprise_for_research"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    name: Mapped[str] = mapped_column(unique=True)
    base_research = relationship("BaseResearch", back_populates="enterprise_for_research")
    special_research = relationship("SpecialResearch", back_populates="enterprise_for_research")
    exclude_product = relationship("ExcludeProducts", back_populates="enterprise_for_research")


class BaseResearch(Base):
    __tablename__ = "base_research"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    sampling_number: Mapped[str] = mapped_column(nullable=True)
    sampling_date: Mapped[str] = mapped_column(nullable=True)
    operator: Mapped[str]
    disease: Mapped[str]
    date_of_research: Mapped[str]
    method: Mapped[str]
    expertise_id: Mapped[str]
    result: Mapped[str]
    conclusion: Mapped[str]
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise_for_research.uuid", ondelete="CASCADE"))
    enterprise_for_research = relationship("EnterpriseForResearch", back_populates="base_research", uselist=False)


class SpecialResearch(Base):
    __tablename__ = "special_research"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    product: Mapped[str]
    sampling_number: Mapped[str] = mapped_column(nullable=True)
    sampling_date: Mapped[str] = mapped_column(nullable=True)
    operator: Mapped[str]
    disease: Mapped[str]
    date_of_research: Mapped[str]
    method: Mapped[str] = mapped_column(nullable=True)
    expertise_id: Mapped[str]
    result: Mapped[str]
    conclusion: Mapped[str]
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise_for_research.uuid", ondelete="CASCADE"))
    enterprise_for_research = relationship("EnterpriseForResearch", back_populates="special_research", uselist=False)


class ExcludeProducts(Base):
    __tablename__ = "exclude_products"

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4, nullable=False)
    product: Mapped[str]
    enterprise_uuid: Mapped[UUID] = mapped_column(ForeignKey("enterprise_for_research.uuid", ondelete="CASCADE"))
    enterprise_for_research = relationship("EnterpriseForResearch", back_populates="exclude_product", uselist=False)