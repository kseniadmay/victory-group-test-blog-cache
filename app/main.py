from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import get_db, Base, engine
from app.schemas import PostCreate, PostUpdate, PostResponse
from app.crud import create_post, get_post, update_post, delete_post
from app.cache import get_post_from_cache, set_post_to_cache, invalidate_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-хук приложения. Выполняется при запуске FastAPI

    Создаём таблицы в базе данных (если их ещё нет)
    """
    Base.metadata.create_all(bind=engine)
    yield


# Создаём экземпляр FastAPI приложения
app = FastAPI(
    title='Blog Cache Test API',
    lifespan=lifespan
)


@app.post(
    '/posts/',
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post_endpoint(post: PostCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый пост

    - Принимает данные через Pydantic-схему
    - Использует dependency get_db для получения сессии БД
    - Возвращает созданный пост
    """
    return create_post(db, post)


@app.get('/posts/{post_id}', response_model=PostResponse)
async def get_post_endpoint(post_id: int, db: Session = Depends(get_db)):
    """
    Получает пост по ID с использованием кэширования (Cache-Aside)

    Логика:
    1. Проверяем кэш (Redis)
    2. Если есть, возвращаем (cache hit)
    3. Если нет, берём из БД (cache miss)
    4. Сохраняем в кэш
    5. Возвращаем результат
    """

    # Пытаемся получить данные из кэша
    cached = get_post_from_cache(post_id)
    if cached:
        return cached  # cache hit

    # Если в кэше нет, обращаемся к БД
    post = get_post(db, post_id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail='Пост не найден'
        )

    # Преобразуем результат в dict (так как raw SQL возвращает mapping)
    post_dict = dict(post)

    # Сохраняем в кэш для последующих запросов
    set_post_to_cache(post_dict)

    return post_dict


@app.put('/posts/{post_id}', response_model=PostResponse)
async def update_post_endpoint(
        post_id: int,
        post: PostUpdate,
        db: Session = Depends(get_db)
):
    """
    Обновляет пост

    Логика:
    1. Обновляем данные в БД
    2. Если пост не найден — 404
    3. Инвалидируем кэш (удаляем старые данные)
    4. Возвращаем обновлённый пост
    """
    updated = update_post(db, post_id, post)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail='Пост не найден'
        )

    # Удаляем кэш, чтобы не вернуть устаревшие данные
    invalidate_cache(post_id)

    return updated


@app.delete('/posts/{post_id}')
async def delete_post_endpoint(
        post_id: int,
        db: Session = Depends(get_db)
):
    """
    Удаляет пост

    Логика:
    1. Удаляем пост из БД
    2. Если не найден — 404
    3. Инвалидируем кэш
    4. Возвращаем сообщение об успехе
    """
    deleted = delete_post(db, post_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail='Пост не найден'
        )

    # Удаляем кэш, чтобы не осталось битых данных
    invalidate_cache(post_id)

    return {'message': 'Пост успешно удалён'}
