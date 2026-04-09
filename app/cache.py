import json
import os
import redis
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем URL для подключения к Redis из переменных окружения
REDIS_URL = os.getenv('REDIS_URL')

# Создаём клиент Redis
# decode_responses=True автоматически декодирует байты в строки
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Время жизни кэша в секундах (5 минут)
CACHE_TTL = 300


def get_cache_key(post_id: int) -> str:
    """
    Формирует ключ для хранения поста в Redis

    Используем префикс 'post:' для избежания конфликтов с другими данными в Redis и удобства отладки и чтения ключей
    Пример: post:1
    """
    return f'post:{post_id}'


def get_post_from_cache(post_id: int) -> dict | None:
    """
    Получает пост из кэша Redis

    Логика:
    1. Формируем ключ
    2. Пытаемся получить данные из Redis
    3. Если данные есть, десериализуем JSON в dict
    4. Если нет, возвращаем None

    :param post_id: ID поста
    :return: dict с данными поста или None
    """
    key = get_cache_key(post_id)

    # Пытаемся получить данные из Redis
    data = redis_client.get(key)

    if data:
        # Redis хранит строки — преобразуем обратно в словарь
        return json.loads(data)

    # Если данных нет, кэш пуст (cache miss)
    return None


def set_post_to_cache(post: dict):
    """
    Сохраняет пост в кэш Redis

    Используем setex:
    - сразу устанавливаем значение
    - задаём TTL

    json.dumps используется для сериализации dict-строка, так как Redis хранит данные в виде строк

    default=str нужен для корректной сериализации нестандартных типов (datetime)

    :param post: словарь с данными поста
    """
    key = get_cache_key(post['id'])

    redis_client.setex(
        key,
        CACHE_TTL,
        json.dumps(post, default=str)
    )


def invalidate_cache(post_id: int):
    """
    Инвалидирует кэш для конкретного поста. Используется при обновлении и удалении поста

    :param post_id: ID поста
    """
    key = get_cache_key(post_id)

    # Удаляем ключ из Redis
    redis_client.delete(key)
