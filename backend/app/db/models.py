from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    conditions = Column(Text)   # stored as comma-separated
    history = Column(Text)

class Trial(Base):
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True, index=True)
    nct_id = Column(String, index=True)
    title = Column(Text)
    condition = Column(String)
    text = Column(Text)
    eligibility = Column(Text)