# config.py
import os

# Токен вашего Telegram-бота
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Абсолютный путь к корневой директории проекта (где лежит config.py)
basedir = os.path.abspath(os.path.dirname(__file__))

# Строка подключения к базе данных для SQLAlchemy.
# Файл базы данных будет создан/использоваться в корневом каталоге проекта.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')

# Дополнительные настройки (например, для логирования)
LOG_LEVEL = "INFO"

# Часовой пояс
LOCAL_TIMEZONE = "Europe/Moscow"
