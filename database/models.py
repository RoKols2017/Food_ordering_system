from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

# Определяем локальный часовой пояс (замените на нужный вам, если необходимо)
LOCAL_TIMEZONE = pytz.timezone("Europe/Moscow")

def local_now():
    """Возвращает текущее время с учетом локального часового пояса."""
    return datetime.now(LOCAL_TIMEZONE)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime(timezone=True), default=local_now)

    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    address = Column(String)
    phone = Column(String)
    created_at = Column(DateTime(timezone=True), default=local_now)

    categories = relationship("Category", back_populates="restaurant")
    dishes = relationship("Dish", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)

    restaurant = relationship("Restaurant", back_populates="categories")
    dishes = relationship("Dish", back_populates="category")


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=local_now)

    category = relationship("Category", back_populates="dishes")
    restaurant = relationship("Restaurant", back_populates="dishes")
    order_items = relationship("OrderItem", back_populates="dish")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    order_date = Column(DateTime(timezone=True), default=local_now)
    status = Column(String, nullable=False, default='new')  # 'cart', 'new', 'processing', 'completed', 'cancelled'
    total_cost = Column(Float)
    payment_method = Column(String)  # 'online', 'cash'
    comment = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=local_now)

    user = relationship("User", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    dish_id = Column(Integer, ForeignKey('dishes.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    note = Column(Text)

    order = relationship("Order", back_populates="order_items")
    dish = relationship("Dish", back_populates="order_items")


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), default=local_now)

    user = relationship("User", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")


def init_db(engine):
    """Создаёт таблицы в базе данных"""
    Base.metadata.create_all(engine)
