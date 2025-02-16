# handlers/menu.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Глобальная переменная для экземпляра базы данных (будет установлена извне)
db = None

def set_db(db_instance):
    """
    Устанавливает глобальный экземпляр базы данных для данного модуля.
    """
    global db
    db = db_instance

def get_category_by_id(category_id):
    """
    Возвращает категорию по ее ID, выполняя запрос через сессию.
    """
    session = db.Session()
    try:
        from database.models import Category
        category = session.query(Category).filter_by(id=category_id).first()
        return category
    except Exception as e:
        logging.error("Ошибка при получении категории: %s", e)
        return None
    finally:
        session.close()

def register_handlers(bot):
    # Первый уровень: выбор ресторана
    @bot.message_handler(commands=['menu'])
    def menu_handler(message):
        restaurants = db.get_restaurants()
        if not restaurants:
            bot.send_message(message.chat.id, "Меню пока недоступно.")
            return
        markup = InlineKeyboardMarkup()
        for restaurant in restaurants:
            markup.add(InlineKeyboardButton(
                text=restaurant.name,
                callback_data=f"restaurant_{restaurant.id}"
            ))
        bot.send_message(message.chat.id, "Выберите ресторан:", reply_markup=markup)

    # Обработчик выбора ресторана
    @bot.callback_query_handler(func=lambda call: call.data.startswith("restaurant_"))
    def restaurant_callback(call):
        try:
            restaurant_id = int(call.data.split('_')[1])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "Ошибка в данных ресторана.")
            return
        restaurant = next((r for r in db.get_restaurants() if r.id == restaurant_id), None)
        if not restaurant:
            bot.answer_callback_query(call.id, "Ресторан не найден.")
            return
        categories = db.get_categories(restaurant_id)
        if not categories:
            bot.send_message(call.message.chat.id, "Категории отсутствуют.")
            return
        markup = InlineKeyboardMarkup()
        for category in categories:
            markup.add(InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.id}"
            ))
        # Кнопка "Назад" для возврата к выбору ресторана
        markup.add(InlineKeyboardButton(text="Назад", callback_data="back_to_restaurants"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Меню ресторана {restaurant.name}:",
            reply_markup=markup
        )

    # Обработчик возврата к выбору ресторана
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_restaurants")
    def back_to_restaurants(call):
        restaurants = db.get_restaurants()
        if not restaurants:
            bot.send_message(call.message.chat.id, "Меню пока недоступно.")
            return
        markup = InlineKeyboardMarkup()
        for restaurant in restaurants:
            markup.add(InlineKeyboardButton(
                text=restaurant.name,
                callback_data=f"restaurant_{restaurant.id}"
            ))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите ресторан:",
            reply_markup=markup
        )

    # Обработчик выбора категории
    @bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
    def category_callback(call):
        try:
            category_id = int(call.data.split('_')[1])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "Ошибка в данных категории.")
            return
        category = get_category_by_id(category_id)
        if not category:
            bot.answer_callback_query(call.id, "Категория не найдена.")
            return
        dishes = db.get_dishes(category_id)
        if not dishes:
            bot.send_message(call.message.chat.id, "В этой категории нет блюд.")
            return
        markup = InlineKeyboardMarkup()
        for dish in dishes:
            markup.add(InlineKeyboardButton(
                text=f"{dish.name} - {dish.price} руб.",
                callback_data=f"dish_{dish.id}"
            ))
        # Кнопка "Назад" для возврата к списку категорий ресторана
        markup.add(InlineKeyboardButton(
            text="Назад",
            callback_data=f"back_to_categories_{category.restaurant_id}"
        ))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите блюдо:",
            reply_markup=markup
        )

    # Обработчик возврата к списку категорий ресторана
    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_categories_"))
    def back_to_categories(call):
        parts = call.data.split('_')
        # Ожидаемый формат: ["back", "to", "categories", "{restaurant_id}"]
        if len(parts) < 4 or not parts[3].isdigit():
            bot.answer_callback_query(call.id, "Ошибка в данных возврата.")
            return
        restaurant_id = int(parts[3])
        restaurant = next((r for r in db.get_restaurants() if r.id == restaurant_id), None)
        if not restaurant:
            bot.answer_callback_query(call.id, "Ресторан не найден.")
            return
        categories = db.get_categories(restaurant_id)
        if not categories:
            bot.send_message(call.message.chat.id, "Категории отсутствуют.")
            return
        markup = InlineKeyboardMarkup()
        for category in categories:
            markup.add(InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.id}"
            ))
        markup.add(InlineKeyboardButton(text="Назад", callback_data="back_to_restaurants"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Меню ресторана {restaurant.name}:",
            reply_markup=markup
        )

    # Обработчик выбора блюда
    @bot.callback_query_handler(func=lambda call: call.data.startswith("dish_"))
    def dish_callback(call):
        try:
            dish_id = int(call.data.split('_')[1])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "Ошибка в данных блюда.")
            return
        dish = db.get_dish(dish_id)
        if not dish:
            bot.answer_callback_query(call.id, "Блюдо не найдено.")
            return
        text = (f"Блюдо: {dish.name}\n"
                f"Цена: {dish.price} руб.\n"
                f"Описание: {dish.description or 'Описание отсутствует'}")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            text="Добавить в заказ",
            callback_data=f"add_{dish.id}"
        ))
        # Кнопка "Назад" для возврата к списку блюд выбранной категории
        markup.add(InlineKeyboardButton(
            text="Назад",
            callback_data=f"back_to_category_{dish.category_id}"
        ))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup
        )

    # Обработчик возврата к списку блюд выбранной категории
    @bot.callback_query_handler(func=lambda call: call.data.startswith("back_to_category_"))
    def back_to_dish_list(call):
        parts = call.data.split('_')
        # Ожидаемый формат: ["back", "to", "category", "{category_id}"]
        if len(parts) < 4 or not parts[3].isdigit():
            bot.answer_callback_query(call.id, "Ошибка в данных возврата.")
            return
        category_id = int(parts[3])
        dishes = db.get_dishes(category_id)
        if not dishes:
            bot.send_message(call.message.chat.id, "В этой категории нет блюд.")
            return
        category = get_category_by_id(category_id)
        markup = InlineKeyboardMarkup()
        for dish in dishes:
            markup.add(InlineKeyboardButton(
                text=f"{dish.name} - {dish.price} руб.",
                callback_data=f"dish_{dish.id}"
            ))
        markup.add(InlineKeyboardButton(
            text="Назад",
            callback_data=f"back_to_categories_{category.restaurant_id}"
        ))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите блюдо:",
            reply_markup=markup
        )

    # Обработчик добавления блюда в заказ
    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
    def add_callback(call):
        try:
            dish_id = int(call.data.split('_')[1])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "Ошибка в данных блюда.")
            return
        bot.answer_callback_query(call.id, "Блюдо добавлено в заказ.")
        dish = db.get_dish(dish_id)
        if not dish:
            bot.send_message(call.message.chat.id, "Блюдо не найдено.")
            return
        text = (f"Блюдо: {dish.name}\n"
                f"Цена: {dish.price} руб.\n"
                f"Описание: {dish.description or 'Описание отсутствует'}")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            text="Назад",
            callback_data=f"back_to_category_{dish.category_id}"
        ))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup
        )
