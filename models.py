import os
import datetime

import dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Text, DateTime, func

CONFIGURATION = dotenv.dotenv_values('.env')

POSTGRES_PASSWORD = CONFIGURATION['POSTGRES_PASSWORD']
POSTGRES_USER = CONFIGURATION['POSTGRES_USER']
POSTGRES_DB = CONFIGURATION['POSTGRES_DB']
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')

PG_DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_async_engine(PG_DSN)

Session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

 
class Advertisement(Base):
    __tablename__ = 'ads'

    id: Mapped[int] = mapped_column(primary_key=True)
    header: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def dict(self) -> dict:
        return {
            'id': self.id,
            'header': self.header,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
