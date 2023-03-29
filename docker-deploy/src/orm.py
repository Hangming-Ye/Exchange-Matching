from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Double, Sequence, REAL, Enum, BIGINT
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class StatusEnum(enum.Enum):
    open = 1
    canceled = 2
    executed = 3

class Account(Base):
    __tablename__ = 'account'
    account_id = Column(Integer, Sequence('account_id_seq'), primary_key = True)
    balance = Column(REAL)

class Order(Base):
    __tablename__ = 'order'
    tran_id = Column(Integer, Sequence('tran_id_seq'), primary_key = True)
    symbol = Column(String(256))
    remain_amount = Column(REAL)
    limit_price = Column(REAL)
    status = Column(Enum(StatusEnum))
    time = Column(BIGINT)
    account_id = Column(Integer, ForeignKey('account.account_id',ondelete="SET NULL", onupdate="CASCADE"))

class Executed(Base):
    __tablename__ = 'executed'
    executed_id = Column(Integer, Sequence('executed_id_seq'), primary_key = True)
    order_id = Column(Integer, ForeignKey('order.tran_id',ondelete="SET NULL", onupdate="CASCADE"))
    price = Column(REAL)
    time = Column(BIGINT)

class Position(Base):
    __tablename__ = 'position'
    position_id = Column(Integer, Sequence('position_id_seq'), primary_key = True)
    account_id = Column(Integer, ForeignKey('account.account_id',ondelete="SET NULL", onupdate="CASCADE"))
    amount = Column(REAL)
    symbol = Column(String(256))