from sqlalchemy import Column, Integer, String, BigInteger, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=False)
    alert_price = Column(Float, nullable=True)

class TrackedWallet(Base):
    __tablename__ = "tracked_wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    address = Column(String, nullable=False)