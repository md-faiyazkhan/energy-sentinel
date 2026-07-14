from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    FastAPI dependency — yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables defined in ORM models.
    Called once on application startup.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")