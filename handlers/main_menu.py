from telebot import TeleBot, types
import logging
from handlers import order_utils

db = None

def set_db(db_instance):
    global db
    db = db_instance

def send_main_menu(bot: TeleBot, chat_id: int):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Выбрать ресторан", callback_data="main_select_restaurant"),
        types.InlineKeyboardButton("Корзина", callback_data="main_view_cart")
    )
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['main_menu'])
    def main_menu_handler(message: types.Message):
        send_main_menu(bot, message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "main_select_restaurant")
    def select_restaurant_handler(call: types.CallbackQuery):
        try:
            restaurants = db.get_restaurants()
            if not restaurants:
                bot.answer_callback_query(call.id, "Рестораны отсутствуют.")
                return
            markup = types.InlineKeyboardMarkup()
            for restaurant in restaurants:
                markup.add(types.InlineKeyboardButton(
                    text=restaurant.name,
                    callback_data=f"restaurant_{restaurant.id}"
                ))
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Выберите ресторан:",
                                  reply_markup=markup)
        except Exception as e:
            logging.error("Ошибка в select_restaurant_handler: %s", e)
            bot.answer_callback_query(call.id, "Ошибка при выборе ресторана.")

    @bot.callback_query_handler(func=lambda call: call.data == "main_view_cart")
    def view_cart_handler(call: types.CallbackQuery):
        try:
            text, markup = order_utils.get_cart_details_markup(db, call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=markup)
        except Exception as e:
            logging.error("Ошибка в view_cart_handler: %s", e)
            bot.answer_callback_query(call.id, "Ошибка при просмотре корзины.")
