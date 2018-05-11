from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    api_key = Column(String)
    api_secret = Column(String)
    account = relationship('BinanceAcct', back_populates='user')


class BinanceAcct(Base):
    __tablename__ = 'binanceaccount'
    id = Column(Integer, autoincrement=True, primary_key=True)
    makerCommission = Column(Integer)
    takerCommission = Column(Integer)
    buyerCommission = Column(Integer)
    sellerCommission = Column(Integer)
    canTrade = Column(Boolean)
    canWithdraw = Column(Boolean)
    canDeposit = Column(Boolean)
    updateTime = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='account')
    balances = relationship('Balance', back_populates='account')

    def __repr__(self):
        return f'<User({self.id} balances: {len(self.balances)}>'


class Balance(Base):
    __tablename__ = 'balance'
    id = Column(Integer, autoincrement=True, primary_key=True)
    asset = Column(String)
    free = Column(Float)
    locked = Column(Float)
    account_id = Column(Integer, ForeignKey('binanceaccount.id'))
    account = relationship('BinanceAcct', back_populates='balances')

    def total(self):
        return self.free + self.locked

    def __repr__(self):
        return f'<Balance({self.id} asset: {self.asset} user: {self.user.id}'
