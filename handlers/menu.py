from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Глобальная переменная для экземпляра базы данных (будет установлена извне)
db = None

def set_db(db_instance):
    """
    Устанавливает глобальный экземпляр базы данных для данного модуля.
    """
    global db
    db = db_instance

def register_handlers(bot):
    @bot.message_handler(commands=['menu'])
    def menu_handler(message):
        # Получаем список ресторанов
        restaurants = db.get_restaurants()
        if not restaurants:
            bot.send_message(message.chat.id, "Меню пока недоступно.")
            return

        # Если ресторанов несколько, можно сделать выбор; для простоты выберем первый
        restaurant = restaurants[0]
        categories = db.get_categories(restaurant.id)
        if not categories:
            bot.send_message(message.chat.id, "Меню пока недоступно.")
            return

        markup = InlineKeyboardMarkup()
        for category in categories:
            markup.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
        bot.send_message(message.chat.id, f"Меню ресторана {restaurant.name}:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
    def category_callback(call):
        category_id = int(call.data.split('_')[1])
        dishes = db.get_dishes(category_id)
        if not dishes:
            bot.answer_callback_query(call.id, "В этой категории нет блюд.")
            return
        markup = InlineKeyboardMarkup()
        for dish in dishes:
            markup.add(InlineKeyboardButton(text=f"{dish.name} - {dish.price} руб.", callback_data=f"dish_{dish.id}"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Выберите блюдо:",
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('dish_'))
    def dish_callback(call):
        dish_id = int(call.data.split('_')[1])
        dish = db.get_dish(dish_id)
        if not dish:
            bot.answer_callback_query(call.id, "Ошибка при получении информации о блюде.")
            return
        text = (f"Блюдо: {dish.name}\n"
                f"Цена: {dish.price} руб.\n"
                f"Описание: {dish.description or 'Описание отсутствует'}")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Добавить в заказ", callback_data=f"add_{dish.id}"))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
    def add_callback(call):
        dish_id = int(call.data.split('_')[1])
        # Здесь можно добавить логику добавления блюда в заказ (корзину)
        bot.answer_callback_query(call.id, "Блюдо добавлено в заказ.")
        bot.send_message(call.message.chat.id, "Блюдо добавлено в заказ.")
