import logging
from database.db import Database
from database.models import Restaurant, Category, Dish

def populate_categories_dishes():
    db = Database()
    session = db.Session()
    try:
        # Ищем ресторан "Токио Сити" по имени
        restaurant = session.query(Restaurant).filter_by(name="Токио Сити").first()
        if not restaurant:
            logging.error("Ресторан 'Токио Сити' не найден в базе данных.")
            return

        # Определяем данные для категорий
        categories_data = [
            {"name": "Суши", "description": "Свежие суши с рыбой и морепродуктами."},
            {"name": "Роллы", "description": "Разнообразные роллы по японским рецептам."},
            {"name": "Сеты", "description": "Наборы популярных блюд."},
            {"name": "Горячие блюда", "description": "Теплые блюда японской кухни."},
        ]
        # Словарь для хранения созданных категорий по имени
        categories_dict = {}
        for cat in categories_data:
            category = Category(
                name=cat["name"],
                description=cat["description"],
                restaurant_id=restaurant.id
            )
            session.add(category)
            # Обновляем сессию, чтобы получить сгенерированный ID
            session.flush()
            categories_dict[cat["name"]] = category

        # Определяем данные для блюд
        dishes_data = [
            # Для категории "Суши"
            {
                "name": "Суши с лососем",
                "description": "Нежные суши с ломтиками свежего лосося.",
                "price": 500,
                "category": "Суши"
            },
            {
                "name": "Суши с тунцом",
                "description": "Суши с тунцом и легким соевым соусом.",
                "price": 550,
                "category": "Суши"
            },
            # Для категории "Роллы"
            {
                "name": "Калифорния ролл",
                "description": "Ролл с крабом, авокадо и огурцом.",
                "price": 600,
                "category": "Роллы"
            },
            {
                "name": "Дракон ролл",
                "description": "Ролл с угрем, авокадо и кунжутом.",
                "price": 700,
                "category": "Роллы"
            },
            # Для категории "Сеты"
            {
                "name": "Сет классический",
                "description": "Набор из лучших блюд ресторана.",
                "price": 1500,
                "category": "Сеты"
            },
            # Для категории "Горячие блюда"
            {
                "name": "Терияки курица",
                "description": "Курица в соусе терияки с рисом.",
                "price": 800,
                "category": "Горячие блюда"
            },
        ]

        # Добавляем блюда, связывая их с соответствующими категориями и рестораном
        for dish_data in dishes_data:
            category_name = dish_data.pop("category")
            category = categories_dict.get(category_name)
            if category:
                dish = Dish(
                    name=dish_data["name"],
                    description=dish_data["description"],
                    price=dish_data["price"],
                    category_id=category.id,
                    restaurant_id=restaurant.id,
                    available=True
                )
                session.add(dish)
            else:
                logging.warning(f"Категория '{category_name}' не найдена для блюда '{dish_data['name']}'.")

        session.commit()
        logging.info("Категории и блюда для 'Токио Сити' успешно добавлены в базу данных.")
    except Exception as e:
        session.rollback()
        logging.error("Ошибка при заполнении таблиц: %s", e)
    finally:
        session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    populate_categories_dishes()
