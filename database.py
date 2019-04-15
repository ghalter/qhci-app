"""

"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Integer, Float, Column, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()
db = SQLAlchemy()

import json

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    entries = relationship("DataEntry", back_populates="folders")

class DataEntry(Base):
    """
    """
    __tablename__ = 'data_entries'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"))
    set_slope = Column(Float, nullable=False)
    true_slope = Column(Float, nullable=False)

    user = relationship("User", back_populates="folders")





Base = declarative_base()
db = SQLAlchemy()