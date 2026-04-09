# BLOG CACHE API

REST API для блога с кэшированием популярных постов. Проект демонстрирует production-ready подход к кэшированию в FastAPI: проверка Redis → miss → PostgreSQL → запись в кэш + автоматическая инвалидация при изменениях. Реализовано на FastAPI с использованием SQLAlchemy (raw SQL), Redis и Docker Compose.

**Swagger документация**:  
http://localhost:8000/docs

## Стек технологий

- Python 3.14
- FastAPI 0.135
- SQLAlchemy 2.0
- PostgreSQL 16
- Redis 7.4
- Docker Compose 5.1
- pytest + TestClient

## Возможности

### Основные функции

- CRUD операций с постами
- Кэширование популярных постов в Redis
- Автоматическая инвалидация кэша при обновлении и удалении
- Raw SQL запросы к PostgreSQL
- Полная обработка ошибок и валидация

### Системные возможности

- Запуск одной командой через Docker Compose
- Чистая структура проекта
- Интеграционный тест, проверяющий логику кэширования

## Endpoints

`POST /posts/` – создать новый пост  
`GET /posts/{post_id}` – получить пост (с кэшированием)  
`PUT /posts/{post_id}` – обновить пост + инвалидация кэша  
`DELETE /posts/{post_id}` – удалить пост + инвалидация кэша

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/kseniadmay/victory-group-test-blog-cache.git
cd victory-group-test-blog-cache
```

### 2. Запуск через Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

API будет доступно по адресу: http://localhost:8000/docs

## Тестирование

```bash
# Запуск теста внутри контейнера
docker-compose exec app pytest -v
```

## Ключевые решения

- Кэширование – Cache-Aside паттерн (Redis → miss → PostgreSQL → cache)
- Инвалидация кэша – мгновенная при PUT/DELETE
- TTL 5 минут – дополнительная страховка от устаревших данных
- Raw SQL – используется в методе get_post
- Redis – синхронный клиент – обеспечивает стабильную работу тестов и простоту запуска
- FastAPI – async-эндпоинты там, где это уместно
- Docker Compose – все сервисы (app + PostgreSQL + Redis) запускаются одной командой

## Архитектура кэширования

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│   FastAPI   │◄────►│    Redis    │
│    (GET)    │      │   (Cache)   │
└──────┬──────┘      └─────────────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │
│     DB      │
└─────────────┘
```

PUT / DELETE → PostgreSQL + Redis.delete (инвалидация)

## Структура проекта

```
blog-cache-test/                 # Корень репозитория
├── app/                         # Основной код приложения
│   ├── main.py                  # FastAPI приложение + роуты
│   ├── models.py                # SQLAlchemy модели
│   ├── schemas.py               # Pydantic схемы
│   ├── crud.py                  # CRUD + raw SQL
│   ├── cache.py                 # Логика работы с Redis
│   ├── database.py              # Подключение к БД
│   └── tests/
│       └── test_integration.py  # Интеграционный тест кэширования
├── docker-compose.yml           # Сервисы: app + db + redis
├── Dockerfile                   # Docker образ проекта
├── requirements.txt             # Зависимости для запуска проекта
├── .env.example                 # Шаблон переменных окружения
└── README.md                    # Документация
```

## Автор

GitHub: [@kseniadmay](https://github.com/kseniadmay)  
Email: kseniadmay@gmail.com