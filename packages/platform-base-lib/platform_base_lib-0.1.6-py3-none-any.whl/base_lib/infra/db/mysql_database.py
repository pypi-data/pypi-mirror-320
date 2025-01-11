from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker

from base_lib.configs.config import settings
from base_lib.infra.logger.logger import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


# Database configuration
DATABASE_URI = settings.MYSQL_URI
DATABASE_PREFIX = settings.MYSQL_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session maker
local_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting the database session.
    """
    async_session = local_session
    async with async_session() as db:
        yield db


async def init_db(drop_all: bool = False):
    """
    Initialize the database by creating or altering tables based on defined models.
    """
    async with engine.begin() as conn:
        if drop_all:
            logger.info("Dropping all tables in local environment...")
            await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
