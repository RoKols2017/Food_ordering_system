# database/db.py
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import config
from database.models import Base, User


class Database:
    def __init__(self, db_url=config.SQLALCHEMY_DATABASE_URI):
        # Параметр check_same_thread=False нужен для SQLite при использовании в многопоточном режиме
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        # Создание таблиц (если их ещё нет)
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def register_user(self, message):
        """
        Регистрирует пользователя в базе данных с использованием SQLAlchemy ORM.

        Возвращает:
            bool: True, если пользователь новый, иначе False.
        """
        session = self.Session()
        try:
            telegram_id = message.from_user.id
            username = message.from_user.username or ""
            first_name = message.from_user.first_name or ""
            last_name = message.from_user.last_name or ""

            # Проверяем, существует ли уже пользователь с таким telegram_id
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                logging.info(f"Пользователь {telegram_id} уже существует.")
                return False

            # Создаем нового пользователя
            new_user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(new_user)
            session.commit()
            logging.info(f"Новый пользователь зарегистрирован: {telegram_id}")
            return True
        except Exception as e:
            session.rollback()
            logging.error(f"Ошибка при регистрации пользователя: {e}")
            return False
        finally:
            session.close()

    # Метод: получить список ресторанов
    def get_restaurants(self):
        session = self.Session()
        try:
            from database.models import Restaurant
            restaurants = session.query(Restaurant).all()
            return restaurants
        except Exception as e:
            logging.error("Ошибка получения ресторанов: %s", e)
            return []
        finally:
            session.close()

    # Метод: получить категории по id ресторана
    def get_categories(self, restaurant_id):
        session = self.Session()
        try:
            from database.models import Category
            categories = session.query(Category).filter_by(restaurant_id=restaurant_id).all()
            return categories
        except Exception as e:
            logging.error("Ошибка получения категорий: %s", e)
            return []
        finally:
            session.close()

    # Метод: получить список блюд по id категории
    def get_dishes(self, category_id):
        session = self.Session()
        try:
            from database.models import Dish
            dishes = session.query(Dish).filter_by(category_id=category_id).all()
            return dishes
        except Exception as e:
            logging.error("Ошибка получения блюд: %s", e)
            return []
        finally:
            session.close()

    # Метод: получить данные по конкретному блюду
    def get_dish(self, dish_id):
        session = self.Session()
        try:
            from database.models import Dish
            dish = session.query(Dish).filter_by(id=dish_id).first()
            return dish
        except Exception as e:
            logging.error("Ошибка получения блюда: %s", e)
            return None
        finally:
            session.close()