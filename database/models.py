from sqlalchemy import Column, Integer, String, BigInteger, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=False)

class TrackedWallet(Base):
    __tablename__ = "tracked_wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    address = Column(String, nullable=False)

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    item_name = Column(String, nullable=False)
    remind_at = Column(DateTime, default=datetime.utcnow)