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

    def dto(self):
        ans = dict()
        ans['account_id'] = self.account_id
        ans['balance'] = self.balance
        return ans

class Order(Base):
    __tablename__ = 'order'
    tran_id = Column(Integer, Sequence('tran_id_seq'), primary_key = True)
    symbol = Column(String(256))
    remain_amount = Column(REAL)
    limit_price = Column(REAL)
    status = Column(Enum(StatusEnum))
    time = Column(BIGINT)
    account_id = Column(Integer, ForeignKey('account.account_id',ondelete="SET NULL", onupdate="CASCADE"))
    
    def dto(self):
        ans = dict()
        ans['tran_id'] = self.tran_id
        ans['symbol'] = self.symbol
        ans['remain_amount'] = self.remain_amount
        ans['limit_price'] = self.limit_price
        ans['status'] = self.status.name
        ans['time'] = self.time
        ans['account_id'] = self.account_id
        return ans


class Executed(Base):
    __tablename__ = 'executed'
    executed_id = Column(Integer, Sequence('executed_id_seq'), primary_key = True)
    order_id = Column(Integer, ForeignKey('order.tran_id',ondelete="SET NULL", onupdate="CASCADE"))
    price = Column(REAL)
    amount = Column(REAL)
    time = Column(BIGINT)

    def dto(self):
        ans = dict()
        ans['executed_id'] = self.executed_id
        ans['order_id'] = self.order_id
        ans['price'] = self.price
        ans['amount'] = self.amount
        ans['time'] = self.time
        return ans

class Position(Base):
    __tablename__ = 'position'
    position_id = Column(Integer, Sequence('position_id_seq'), primary_key = True)
    account_id = Column(Integer, ForeignKey('account.account_id',ondelete="SET NULL", onupdate="CASCADE"))
    amount = Column(REAL)
    symbol = Column(String(256))

    def dto(self):
        ans = dict()
        ans['position_id'] = self.position_id
        ans['account_id'] = self.account_id
        ans['amount'] = self.amount
        ans['symbol'] = self.symbol
        return ans