from sqlalchemy import Column, Integer, String
from app.config.database import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    author = Column(String, index=True)
    publisher = Column(String, index=True)
