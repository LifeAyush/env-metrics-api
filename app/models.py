from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Enum, Float, DateTime, Integer

from app.schemas import CategoryEnum 

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    category = Column(Enum(CategoryEnum))
    value = Column(Float)
    unit = Column(String)
    date = Column(DateTime, default=datetime.now)
