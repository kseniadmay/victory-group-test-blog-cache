from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Post(Base):
    """
    ORM-модель поста. Описывает таблицу 'posts' в базе данных. Каждый атрибут класса соответствует колонке в таблице.
    SQLAlchemy автоматически создаёт таблицу на основе этой модели.
    """

    # Имя таблицы в базе данных
    __tablename__ = 'posts'

    # Уникальный идентификатор поста (PRIMARY KEY)
    # index=True — создаёт индекс для ускорения поиска
    id = Column(Integer, primary_key=True, index=True)

    # Заголовок поста
    # String(200) — строка с максимальной длиной 200 символов
    # nullable=False — поле обязательно для заполнения
    # index=True — ускоряет поиск по заголовку
    title = Column(String(200), nullable=False, index=True)

    # Основной текст поста. Text используется для длинных текстов без ограничения по длине
    content = Column(Text, nullable=False)

    # Автор поста. Ограничение в 100 символов
    author = Column(String(100), nullable=False)

    # Дата и время создания поста
    # server_default=func.now() — значение устанавливается на уровне БД при создании записи (текущая дата и время)
    created_at = Column(DateTime, server_default=func.now())
