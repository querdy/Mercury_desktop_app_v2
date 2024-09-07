from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class VetisUser(Base):
    __tablename__ = "vetis_user"

    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
