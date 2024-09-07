import uuid
from alembic import command
from alembic.config import Config
from sqlalchemy import UUID, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = "sqlite:///db.sqlite"
database_path = DATABASE_URL.split(":///")[-1]

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    __abstract__ = True

    uuid: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4, nullable=False)


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


'''
alembic revision --autogenerate -m ""
alembic upgrade head
'''
