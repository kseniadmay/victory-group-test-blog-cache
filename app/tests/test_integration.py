import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_cache_logic():
    response = client.post('/posts/', json={
        'title': 'Тестовый пост',
        'content': 'Контент для проверки кэша',
        'author': 'Ksenia'
    })
    assert response.status_code == 201
    post_id = response.json()['id']

    first = client.get(f'/posts/{post_id}')
    assert first.status_code == 200

    second = client.get(f'/posts/{post_id}')
    assert second.status_code == 200
    assert second.json() == first.json()

    client.put(f'/posts/{post_id}', json={
        'title': 'Обновлённый пост',
        'content': 'Новый контент',
        'author': 'Ksenia'
    })

    after_update = client.get(f'/posts/{post_id}')
    assert after_update.json()['title'] == 'Обновлённый пост'
