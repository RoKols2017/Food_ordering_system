# handlers/start.py
import logging

# Будем получать экземпляр базы данных через функцию set_db
db = None


def set_db(db_instance):
    """
    Устанавливает глобальный экземпляр базы данных.
    """
    global db
    db = db_instance


def register_new_user(message):
    """
    Регистрирует нового пользователя в базе данных.

    Параметры:
        message (telebot.types.Message): Сообщение от пользователя.

    Возвращает:
        bool: True, если регистрация успешна (пользователь новый),
              False, если пользователь уже существует или произошла ошибка.
    """
    try:
        if not hasattr(message, "from_user") or message.from_user is None:
            logging.error("Сообщение не содержит информации о пользователе.")
            return False
        # Метод db.register_user уже логирует результат регистрации, поэтому лишнего логирования здесь не будет.
        is_new_user = db.register_user(message)
        return is_new_user
    except Exception as e:
        user_id = getattr(message.from_user, 'id', 'unknown')
        logging.error(f"Ошибка при регистрации пользователя {user_id}: {e}")
        return False


def get_greeting(is_new_user, first_name):
    """
    Генерирует приветственное сообщение в зависимости от статуса регистрации.
    """
    if is_new_user:
        return f"Привет, {first_name}! Добро пожаловать в наш сервис заказа еды!"
    return f"С возвращением, {first_name}!"


def register_handlers(bot):
    """
    Регистрирует обработчик команды /start.
    """

    @bot.message_handler(commands=['start'])
    def start_command_handler(message):
        try:
            is_new_user = register_new_user(message)
            first_name = message.from_user.first_name if message.from_user and message.from_user.first_name else ""
            greeting = get_greeting(is_new_user, first_name)
            bot.send_message(message.chat.id, greeting)
        except Exception as e:
            user_id = getattr(message.from_user, 'id', 'unknown')
            logging.error(f"Ошибка обработки команды /start для {user_id}: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")
