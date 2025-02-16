# handlers/start.py
import logging
from handlers import main_menu, legal

db = None

def set_db(db_instance):
    global db
    db = db_instance

def register_new_user(message):
    try:
        if not hasattr(message, "from_user") or message.from_user is None:
            logging.error("Сообщение не содержит информации о пользователе.")
            return False
        is_new_user = db.register_user(message)
        return is_new_user
    except Exception as e:
        user_id = getattr(message.from_user, 'id', 'unknown')
        logging.error(f"Ошибка при регистрации пользователя {user_id}: {e}")
        return False

def check_legal_agreement(user_id):
    """
    Проверяет, дал ли пользователь согласие с пользовательским соглашением.
    """
    session = db.Session()
    try:
        from database.models import User
        user = session.query(User).filter_by(telegram_id=user_id).first()
        return user.accepted_terms if user else False
    except Exception as e:
        logging.error("Ошибка при проверке пользовательского соглашения: %s", e)
        return False
    finally:
        session.close()

def get_greeting(is_new_user, first_name):
    if is_new_user:
        return f"Привет, {first_name}! Добро пожаловать в наш сервис заказа еды!"
    return f"С возвращением, {first_name}!"

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start_command_handler(message):
        try:
            is_new_user = register_new_user(message)
            first_name = message.from_user.first_name if message.from_user and message.from_user.first_name else ""
            greeting = get_greeting(is_new_user, first_name)
            bot.send_message(message.chat.id, greeting)
            # Проверяем, дал ли пользователь согласие
            if not check_legal_agreement(message.from_user.id):
                # Если нет – отправляем соглашение и блокируем дальнейшие действия до согласия
                legal.show_legal_agreement(bot, message.chat.id)
            else:
                # Если уже согласился – показываем главное меню
                main_menu.send_main_menu(bot, message.chat.id)
        except Exception as e:
            user_id = getattr(message.from_user, 'id', 'unknown')
            logging.error(f"Ошибка обработки команды /start для {user_id}: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")
