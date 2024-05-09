import uuid
from datetime import date
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, registry
from sqlalchemy import String, Date, Time, func, DateTime, Enum, Integer, ForeignKey, Boolean, UUID, Table, Column, \
    Float, DECIMAL
from sqlalchemy.orm import DeclarativeBase

mapper_registry = registry()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    firstname: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    mobilenamber: Mapped[str] = mapped_column(String(15), nullable=True)
    databirthday: Mapped[date] = mapped_column('databirthday', Date, nullable=True)
    password: Mapped[str] = mapped_column(String(500))
    balance: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    notification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    avatar: Mapped[str] = mapped_column(String(255))
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime(timezone=True),
                                             default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime(timezone=True),
                                             default=func.now(), onupdate=func.now(), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_type_id: Mapped[int] = mapped_column(ForeignKey('user_type.id'))
    user_type: Mapped["UserType"] = relationship("UserType", backref="users", lazy="joined")
    all_avto: Mapped[List["Avto"]] = relationship("Avto", back_populates="user", lazy="joined",
                                                  cascade='save-update, merge, delete')


class UserType(Base):
    __tablename__ = 'user_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), default=1)


class Rate(Base):
    __tablename__ = 'rates'
    id: Mapped[int] = mapped_column(primary_key=True)
    ratename: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    pricetime: Mapped[int] = mapped_column(Integer, nullable=False)


class RateTime(Base):
    __tablename__ = 'ratestime'
    id: Mapped[int] = mapped_column(primary_key=True)
    monday: Mapped[bool] = mapped_column(Boolean, default=False)
    tuesday: Mapped[bool] = mapped_column(Boolean, default=False)
    wednesday: Mapped[bool] = mapped_column(Boolean, default=False)
    thursday: Mapped[bool] = mapped_column(Boolean, default=False)
    friday: Mapped[bool] = mapped_column(Boolean, default=False)
    saturday: Mapped[bool] = mapped_column(Boolean, default=False)
    sunday: Mapped[bool] = mapped_column(Boolean, default=False)
    starttime: Mapped[date] = mapped_column(Time, nullable=True)
    stoptime: Mapped[date] = mapped_column(Time, nullable=True)
    rate_id: Mapped[int] = mapped_column(ForeignKey('rates.id'))
    rate: Mapped["Rate"] = relationship("Rate", backref="ratestime", lazy="joined")


class Avto(Base):
    __tablename__ = 'avto'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    color: Mapped[str] = mapped_column(String(50), nullable=True)
    model: Mapped[str] = mapped_column(String(50), nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_id: Mapped[uuid] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="all_avto", lazy="joined")


class Log(Base):
    __tablename__ = 'logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(50), nullable=True)
    start: Mapped[date] = mapped_column('start', DateTime(timezone=True),
                                        default=func.now(), onupdate=func.now(), nullable=True)
    stop: Mapped[date] = mapped_column('stop', DateTime(timezone=True),
                                       default=func.now(), onupdate=func.now())
    billcash: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    billbalance: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    discount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=True)
    in_parking: Mapped[bool] = mapped_column(Boolean, default=False)
