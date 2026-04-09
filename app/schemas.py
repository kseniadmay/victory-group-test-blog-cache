from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    """
    Базовая схема поста.
    Содержит общие поля для создания и обновления постов:
    - title: заголовок поста
    - content: основной текст поста
    - author: автор поста
    """
    title: str
    content: str
    author: str


class PostCreate(PostBase):
    """
    Схема для создания поста. Наследует все поля из PostBase. Используется при POST-запросе /posts/
    """
    pass


class PostUpdate(PostBase):
    """
    Схема для обновления поста. Наследует все поля из PostBase. Используется при PUT-запросе /posts/{post_id}
    """
    pass


class PostResponse(PostBase):
    """
    Схема ответа для поста. Используется в эндпоинтах для отдачи данных клиенту

    Содержит:
    - id: уникальный идентификатор поста
    - created_at: дата и время создания поста
    """
    id: int
    created_at: datetime

    # model_config from_attributes позволяет создавать Pydantic-модель из ORM объекта
    # Например: PostResponse.from_orm(db_post)
    model_config = {'from_attributes': True}