<<<<<<< HEAD
from sqlalchemy import Column, ForeignKey, Integer, String
from .role import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
=======
from sqlalchemy import Column,Integer,String

from app.database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)

    email = Column(String, unique=True)

    password = Column(String)
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
