import logging
from database.db import Database
from database.models import Restaurant

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def populate_restaurants():
    db = Database()
    session = db.Session()
    try:
        # Создаем объект ресторана "Токио Сити"
        tokyo_city = Restaurant(
            name="Токио Сити",
            description=(
                "Ресторан «Токио Сити» предлагает традиционные блюда японской кухни. "
                "Официальный сайт: https://www.tokyo-city.ru/"
            ),
            address="Москва, ул. Примерная, 1",   # Пример адреса (уточните по сайту)
            phone="+7 (495) 123-45-67"            # Пример телефона (уточните по сайту)
        )
        session.add(tokyo_city)
        session.commit()
        logging.info("Ресторан 'Токио Сити' успешно добавлен в базу данных.")
    except Exception as e:
        session.rollback()
        logging.error("Ошибка при добавлении ресторана: %s", e)
    finally:
        session.close()

if __name__ == '__main__':
    populate_restaurants()
