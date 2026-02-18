from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    pin_hash = Column(String(128), nullable=False)

    def __init__(self, pin):
        self.pin_hash = generate_password_hash(pin)

    def check_pin(self, pin):
        return check_password_hash(self.pin_hash, pin)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    type = Column(String(10), nullable=False) # 'expense' or 'income'

    def __init__(self, name, type):
        self.name = name
        self.type = type

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String(10), nullable=False) # 'income' or 'expense'
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    date = Column(DateTime, default=datetime.datetime.now, nullable=False)
    description = Column(String(200), nullable=True)

    user = relationship('User', backref='transactions')
    category = relationship('Category', backref='transactions')

    def __init__(self, user_id, type, amount, category_id, description=None, date=None):
        self.user_id = user_id
        self.type = type
        self.amount = amount
        self.category_id = category_id
        self.description = description
        if date:
            self.date = date
