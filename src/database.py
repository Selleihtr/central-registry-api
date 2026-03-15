from sqlalchemy import create_engine
from src.models import Base
from src import config
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    config.SQLALCHEMY_DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def create_tables():
    """Создает все таблицы, определенные в Base"""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()