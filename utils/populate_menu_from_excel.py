import os
import logging
import pandas as pd
from database.db import Database
from database.models import Restaurant, Category, Dish


def populate_menu_from_excel_sheets():
    db = Database()
    session = db.Session()
    try:
        # Ищем ресторан "Токио Сити" по имени
        restaurant = session.query(Restaurant).filter_by(name="Токио Сити").first()
        if not restaurant:
            logging.error("Ресторан 'Токио Сити' не найден в базе данных.")
            return

        # Определяем путь к файлу menu.xlsx (файл должен находиться в корне проекта)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(base_dir, 'menu.xlsx')

        # Загружаем Excel-файл
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        logging.info("Найденные листы в Excel: %s", sheet_names)

        for sheet in sheet_names:
            # Используем имя листа как название категории
            category_name = sheet
            # Если необходимо, можно задать описание категории (например, пустую строку или извлечь из данных)
            category_description = ""
            category = Category(
                name=category_name,
                description=category_description,
                restaurant_id=restaurant.id
            )
            session.add(category)
            session.flush()  # Чтобы получить сгенерированный ID категории

            # Читаем данные с текущего листа
            df = pd.read_excel(xls, sheet_name=sheet)

            # Проверяем наличие обязательного столбца 'Dish Name'
            if 'Dish Name' not in df.columns:
                logging.error(f"В листе '{sheet}' не найден обязательный столбец 'Dish Name'")
                continue

            # Для каждой строки листа создаем блюдо
            for _, row in df.iterrows():
                dish_name = row.get('Dish Name')
                dish_description = row.get('Dish Description', "")
                price = row.get('Price')
                # Если столбец 'Image URL' присутствует, извлекаем его, иначе задаем None
                image_url = row.get('Image URL', None) if 'Image URL' in df.columns else None

                dish = Dish(
                    name=dish_name,
                    description=dish_description,
                    price=price,
                    category_id=category.id,
                    restaurant_id=restaurant.id,
                    available=True,
                    image_url=image_url
                )
                session.add(dish)

        session.commit()
        logging.info("Категории и блюда из файла menu.xlsx успешно добавлены для 'Токио Сити'.")
    except Exception as e:
        session.rollback()
        logging.error("Ошибка при заполнении таблиц из Excel: %s", e)
    finally:
        session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    populate_menu_from_excel_sheets()
