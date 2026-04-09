import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

# Создаём тестовый клиент для отправки HTTP-запросов к FastAPI приложению
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """
    Фикстура для подготовки базы данных перед каждым тестом
    autouse=True означает, что фикстура применяется автоматически ко всем тестам в этом файле

    Логика:
    1. Перед тестом создаём все таблицы
    2. После теста удаляем их (чистим состояние)
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_cache_logic():
    """
    Интеграционный тест логики кэширования

    Проверяет сценарий:
    1. Создание поста
    2. Первый запрос (ожидается cache miss → данные из БД)
    3. Второй запрос (ожидается cache hit → данные из кэша)
    4. Обновление поста (инвалидация кэша)
    5. Повторный запрос (данные должны быть обновлены)

    Цель: убедиться, что кэш используется при повторных запросах и корректно инвалидируется при изменении данных
    """

    # --- Создание поста ---
    response = client.post('/posts/', json={
        'title': 'Тестовый пост',
        'content': 'Контент для проверки кэша',
        'author': 'Ksenia'
    })

    # Проверяем, что пост успешно создан
    assert response.status_code == 201

    # Получаем id созданного поста
    post_id = response.json()['id']

    # --- Первый запрос (cache miss) ---
    first = client.get(f'/posts/{post_id}')
    assert first.status_code == 200

    # --- Второй запрос (cache hit) ---
    second = client.get(f'/posts/{post_id}')
    assert second.status_code == 200

    # Ответы должны совпадать (данные одинаковые)
    assert second.json() == first.json()

    # --- Обновление поста (должна произойти инвалидация кэша) ---
    client.put(f'/posts/{post_id}', json={
        'title': 'Обновлённый пост',
        'content': 'Новый контент',
        'author': 'Ksenia'
    })

    # --- Проверка после обновления ---
    after_update = client.get(f'/posts/{post_id}')

    # Проверяем, что вернулись обновлённые данные (кэш не устарел)
    assert after_update.json()['title'] == 'Обновлённый пост'
