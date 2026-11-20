<<<<<<< HEAD
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
=======
from sqlalchemy import Column,Integer,String

from app.database import Base

class Role(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True)
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
