from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем строку подключения к базе данных. Пример: postgresql://user:password@localhost:5432/db_name
DATABASE_URL = os.getenv('DATABASE_URL')

# Создаём движок — основной объект для работы с БД. Он управляет соединениями и отправкой SQL-запросов
engine = create_engine(DATABASE_URL)

# Создаём фабрику сессий. Сессия — объект для взаимодействия с БД (CRUD операции)
SessionLocal = sessionmaker(
    autocommit=False,  # изменения сохраняются только после явного commit()
    autoflush=False,   # отключаем автоматическую отправку изменений в БД
    bind=engine        # привязываем сессии к нашему engine
)

# Базовый класс для всех ORM-моделей. Все модели будут наследоваться от Base
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии БД в FastAPI

    Используется в эндпоинтах через Depends

    Логика:
    1. Создаём новую сессию
    2. Передаём её в эндпоинт
    3. После завершения запроса закрываем сессию

    Это важно, чтобы не было утечек соединений и каждая операция работала в своей сессии

    :yield: объект сессии SQLAlchemy
    """
    db = SessionLocal()

    try:
        # Передаём сессию в обработчик запроса
        yield db
    finally:
        # Гарантированно закрываем сессию (даже при ошибке)
        db.close()
