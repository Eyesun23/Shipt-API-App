from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, ForeignKey, Table, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy import create_engine
import datetime
import json
from passlib.apps import custom_app_context as pwd_context
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        'name' : self.name,
        'description' : self.description
        }

tags = Table('tags',
    Base.metadata,
    Column('category_id', Integer, ForeignKey('category.id')),
    Column('product_id', Integer, ForeignKey('product.id'))
)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer(), primary_key=True)
    category = relationship('Category', secondary=tags,backref=backref('products', lazy='dynamic'),lazy='dynamic')
    orders = relationship("OrderItem", backref='product', lazy=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    @property
    def serialize(self):
        return {
	    'name' : self.name,
	    'description' : self.description,
	    'price' : self.price,
        'categories': json.dumps([cat.name for cat in self.category])
        }

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer(), primary_key=True)
    itemsOrder = relationship('OrderItem', backref='order', lazy=True)
    status = Column(String)
    date = Column(DateTime, nullable=False,
        default=datetime.utcnow)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    @property
    def serialize(self):
        return {
	    'id' : self.id,
        'customer_id': self.customer_id,
        'status' : self.status,
        'date': str(self.date)
        }

class OrderItem(Base):
    __tablename__ = 'orderitem'
    id = Column(Integer, primary_key=True)
    #A product can be sold in decimal amounts (such as weights).
    quantity = Column(Float,nullable=False)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    @property
    def serialize(self):
        return {
        'id' : self.id,
        'order_id' : self.order_id,
        'product_id' : self.product_id,
        'quantity' : self.quantity
        }
    def __init__(self,product_id, order_id, quantity ):
        self.order_id = order_id
        self.product_id    = product_id
        self.quantity = quantity

    def __repr__(self):
        return "Order ID: {}, Quantity: {}, Product: {}".format(self.order_id, self.quantity, self.product.name)


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    orders = relationship('Order', backref='customer', lazy=True)
    name = Column(String)
    email = Column(String)
    @property
    def serialize(self):
        return {
        'id' : self.id,
	    'name' : self.name,
	    'email' : self.email,
        'order history': json.dumps([order.id for order in self.orders])
        }



engine = create_engine('sqlite:///customers.db')


Base.metadata.create_all(engine)
