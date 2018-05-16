from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from . import Base


class Trade(Base):
    __tablename__ = 'trade'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)
    datetime = Column(DateTime)
    symbol = Column(String)
    order = Column(Integer)
    type = Column(String)
    takerOrMaker = Column(String)
    side = Column(String)
    price = Column(Float)
    cost = Column(Float)
    amount = Column(Float)
    account_id = Column(Integer, ForeignKey('binanceacct.id'))
    account = relationship('BinanceAcct', back_populates='trades')
    fee = relationship('Fee', back_populates='trade', uselist=False)


class Fee(Base):
    __tablename__ = 'fee'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cost = Column(Float)
    currency = Column(String)
    trade_id = Column(Integer, ForeignKey('trade.id'))
    trade = relationship('Trade', back_populates='fee')
