from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Post
from app.schemas import PostCreate, PostUpdate


def create_post(db: Session, post: PostCreate):
    """
    Создаёт новый пост в базе данных

    Логика:
    1. Преобразуем Pydantic-схему в словарь
    2. Создаём ORM-объект Post
    3. Добавляем его в сессию
    4. Коммитим изменения (записываем в БД)
    5. Обновляем объект (получаем id и другие поля из БД)

    :param db: сессия SQLAlchemy
    :param post: данные для создания поста (Pydantic схема)
    :return: созданный объект Post
    """
    # Создаём ORM-объект из входных данных
    db_post = Post(**post.model_dump())

    # Добавляем объект в текущую сессию
    db.add(db_post)

    # Сохраняем изменения в базе данных
    db.commit()

    # Обновляем объект (например, чтобы получить сгенерированный id)
    db.refresh(db_post)

    return db_post


def get_post(db: Session, post_id: int):
    """
    Получает пост по ID с использованием raw SQL

    Логика:
    1. Выполняем SQL-запрос
    2. Получаем одну строку результата
    3. Преобразуем её в словарь

    :param db: сессия SQLAlchemy
    :param post_id: ID поста
    :return: dict с данными поста или None
    """
    result = db.execute(
        text('SELECT * FROM posts WHERE id = :id'),
        {'id': post_id}
    )

    # Получаем первую строку результата
    row = result.fetchone()

    # row._mapping — позволяет получить данные как словарь
    return row._mapping if row else None


def update_post(db: Session, post_id: int, post: PostUpdate):
    """
    Обновляет существующий пост

    Логика:
    1. Находим пост в базе
    2. Если найден, обновляем его поля
    3. Коммитим изменения
    4. Обновляем объект

    :param db: сессия SQLAlchemy
    :param post_id: ID поста
    :param post: новые данные (Pydantic схема)
    :return: обновлённый объект Post или None, если не найден
    """
    # Ищем пост по ID
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        # Обновляем поля объекта
        for key, value in post.model_dump().items():
            setattr(db_post, key, value)

        # Сохраняем изменения
        db.commit()

        # Обновляем объект из БД
        db.refresh(db_post)

    return db_post


def delete_post(db: Session, post_id: int):
    """
    Удаляет пост из базы данных

    Логика:
    1. Находим пост
    2. Если найден, удаляем
    3. Коммитим изменения

    :param db: сессия SQLAlchemy
    :param post_id: ID поста
    :return: удалённый объект Post или None, если не найден
    """
    # Ищем пост по ID
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        # Удаляем объект из сессии
        db.delete(db_post)

        # Применяем изменения в БД
        db.commit()

    return db_post
