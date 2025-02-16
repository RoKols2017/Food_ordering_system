# config.py

# Токен вашего Telegram-бота
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Строка подключения к базе данных для SQLAlchemy.
# В данном случае используется база данных SQLite, расположенная в файле "database.db" в корневой директории проекта.
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

# Дополнительные настройки (например, для логирования)
LOG_LEVEL = "INFO"
