# SQL Alchemy models declaration.
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# mapped_column syntax from SQLAlchemy 2.0.

# https://alembic.sqlalchemy.org/en/latest/tutorial.html
# Note, it is used by alembic migrations logic, see `alembic/env.py`

# Alembic shortcuts:
# # create migration
# alembic revision --autogenerate -m "migration_name"

# # apply all migrations
# alembic upgrade head


import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Temperature(Base):
    __tablename__ = "temperature"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    temperature: Mapped[float] = mapped_column(String(10), nullable=False)


class Humidity(Base):
    __tablename__ = "humidity"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    humidity: Mapped[float] = mapped_column(String(6), nullable=False)


class Pressure(Base):
    __tablename__ = "pressure"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pressure: Mapped[float] = mapped_column(String(10), nullable=False)
