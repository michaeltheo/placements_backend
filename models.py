from database import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    AM = Column(String, unique=True, index=True)
    role = Column(String, default='student')



