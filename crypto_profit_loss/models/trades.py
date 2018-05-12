from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from . import Base


class Trade(Base):
    __tablename__ = 'trade'
    id = Column(Integer, primary_key=True)
    commission = Column(Integer)
    commissionAsset = Column(String)
    isBestMatch = Column(Boolean)
    isBuyer = Column(Boolean)
    isMaker = Column(Boolean)
    orderId = Column(Integer)
    price = Column(Float)
    qty = Column(Float)
    time = Column(Integer)
    account_id = Column(Integer, ForeignKey('binanceacct.id'))
    account = relationship('BinanceAcct', back_populates='trades')

