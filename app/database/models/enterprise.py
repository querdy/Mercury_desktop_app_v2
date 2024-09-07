from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base


class Enterprise(Base):
    __tablename__ = "enterprise"

    name: Mapped[str] = mapped_column(unique=True)
    pk: Mapped[str]
    research = relationship("Research", back_populates="enterprise")
    exclude_product = relationship("ExcludeProducts", back_populates="enterprise")
    immunization = relationship("Immunization", back_populates="enterprise")
