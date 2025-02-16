# handlers/legal.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

db = None

def set_db(db_instance):
    global db
    db = db_instance

def show_legal_agreement(bot, chat_id):
    """
    Отправляет пользователю сообщение с пользовательским соглашением и кнопкой для согласия.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Принимаю", callback_data="legal_accept"))
    text = "Я ознакомлен с содержанием пользовательского соглашения и принимаю условия обработки персональных данных"
    bot.send_message(chat_id, text, reply_markup=markup)

def register_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "legal_accept")
    def legal_accept_handler(call):
        session = db.Session()
        try:
            from database.models import User
            user = session.query(User).filter_by(telegram_id=call.from_user.id).first()
            if user:
                user.accepted_terms = True
                session.commit()
                bot.answer_callback_query(call.id, "Спасибо за согласие!")
                # После согласия переходим к главному меню
                from handlers import main_menu
                main_menu.send_main_menu(bot, call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, "Пользователь не найден.")
        except Exception as e:
            session.rollback()
            logging.error("Ошибка при сохранении согласия пользователя: %s", e)
            bot.answer_callback_query(call.id, "Ошибка при сохранении согласия.")
        finally:
            session.close()
