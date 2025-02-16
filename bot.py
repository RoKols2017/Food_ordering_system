#bot.py
import telebot
import config
import logging
from handlers import start, menu
from database.db import Database

# Централизованная настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Инициализация бота
bot = telebot.TeleBot(config.TOKEN)

# Инициализация базы данных через SQLAlchemy
db = Database()

# Передаём экземпляр базы данных в обработчики
start.set_db(db)
menu.set_db(db)

# Регистрируем обработчики
start.register_handlers(bot)
menu.register_handlers(bot)

if __name__ == '__main__':
    import logging
    logging.getLogger('telebot').setLevel(logging.CRITICAL)
    try:
        logging.info("Запуск бота...")
        bot.infinity_polling()
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем.")
    except Exception as e:
        logging.error("Ошибка при запуске бота: %s", e)
