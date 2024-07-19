import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


DATABASE_URL = "sqlite:///db.sqlite"
database_path = DATABASE_URL.split(":///")[-1]

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# if not os.path.exists(database_path):
#     Base.metadata.create_all(bind=engine)
#     run_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


'''
alembic revision --autogenerate -m ""
alembic upgrade head
'''
