# Контрольная работа №5 – Технологии разработки серверных приложений

**Студент:** Коршиков Руслан Алексеевич  
**Группа:** ЭФБО-06-24

---

## Описание проекта

Проект представляет собой многофункциональное FastAPI-приложение, реализующее:

1. **REST API для управления задачами** (с фильтрацией, статусами, приоритетами, авторизацией через заголовки)
2. **WebSocket чат с комнатами** (обмен сообщениями, уведомления о подключении/отключении)
3. **Ролевую модель** (обычный пользователь / администратор) с разграничением доступа
4. **Контейнеризацию** (Docker, docker-compose)
5. **Интеграционные тесты** (pytest, покрытие всех сценариев)

---

## Запуск проекта

### Локальный запуск (без Docker)

```bash
#клон репозитория
git clone <url-репозитория>
cd kr5_korshikov_ruslan_efbo-06-24

#создание виртуального окружения
python -m venv .venv
source .venv/bin/activate      #Linux/Mac
.venv\Scripts\activate         #Windows

#установить зависимости
pip install -r requirements.txt

#запустить сервер
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: `http://127.0.0.1:8000`

### Запуск через Docker

```bash
docker compose up --build
```

Контейнер будет слушать порт `8000` на хосте.

### Запуск тестов

```bash
pytest -v
```

Все тесты должны проходить успешно.

---

## API Эндпоинты

### Задачи (требуется заголовок `X-User-Id: <int>`)

| Метод | Эндпоинт | Описание | Статусы |
|-------|----------|----------|---------|
| POST | `/tasks` | Создать задачу | 201, 422, 401 |
| GET | `/tasks` | Список задач текущего пользователя (фильтры: `status`, `min_priority`) | 200 |
| GET | `/tasks/{id}` | Получить задачу по ID | 200, 404 |
| PATCH | `/tasks/{id}/status` | Изменить статус задачи | 200, 404 |
| DELETE | `/tasks/{id}` | Удалить свою задачу | 204, 404 |

### Пользователи

| Метод | Эндпоинт | Описание | Статусы |
|-------|----------|----------|---------|
| GET | `/users/me` | Информация о текущем пользователе (из заголовка) | 200, 401 |
| GET | `/users/{id}` | Информация о пользователе (упрощённо) | 200 |

### Администратор (требуется заголовок `X-User-Role: admin`)

| Метод | Эндпоинт | Описание | Статусы |
|-------|----------|----------|---------|
| GET | `/admin/stats` | Статистика по всем задачам | 200, 403 |
| DELETE | `/admin/tasks/{id}` | Удалить любую задачу (даже чужую) | 204, 404, 403 |

### WebSocket чат

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| WS | `/ws/rooms/{room_id}?username={name}` | Подключиться к комнате чата |
| GET | `/rooms/{room_id}/users` | Получить список активных пользователей комнаты |

### Вспомогательные

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/health` | Проверка состояния приложения |

---

## Примеры запросов

### Создание задачи

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 10" \
  -d '{"title":"Купить хлеб","priority":3,"status":"todo"}'
```

### Получение списка задач с фильтром

```bash
curl "http://localhost:8000/tasks?status=todo&min_priority=2" -H "X-User-Id: 10"
```

### Изменение статуса

```bash
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 10" \
  -d '{"status":"done"}'
```

### Удаление задачи (администратор)

```bash
curl -X DELETE http://localhost:8000/admin/tasks/1 -H "X-User-Id: 1" -H "X-User-Role: admin"
```

### Статистика (администратор)

```bash
curl http://localhost:8000/admin/stats -H "X-User-Id: 1" -H "X-User-Role: admin"
```

### WebSocket подключение

```bash
wscat -c "ws://localhost:8000/ws/rooms/python?username=alice"
```

После подключения отправляйте JSON:

```json
{"type":"message","text":"Привет всем!"}
```

Сервер рассылает сообщение всем участникам комнаты в формате:

```json
{"type":"message","room_id":"python","username":"alice","text":"Привет всем!"}
```

---

## Структура проекта

```
kr5_korshikov_ruslan_efbo-06-24/
├── app/
│   ├── __init__.py
│   ├── main.py                 
│   ├── dependencies.py          
│   ├── schemas.py              
│   ├── storage.py               
│   ├── websocket_manager.py   
│   └── routers/
│       ├── __init__.py
│       ├── tasks.py            
│       ├── users.py            
│       └── admin.py            
├── tests/
│   ├── __init__.py
│   ├── test_tasks.py          
│   ├── test_websocket.py 
│   └── test_dependencies_and_routing.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Технологии

- **FastAPI** – веб-фреймворк
- **Pydantic** – валидация данных
- **pytest + pytest-asyncio** – тестирование
- **httpx** – асинхронный HTTP-клиент для тестов
- **websockets** – поддержка WebSocket
- **Docker** – контейнеризация

---

## Статус выполнения требований

| Задание | Требование | Выполнено |
|---------|-----------|-----------|
| 1 | API задач (CRUD, фильтрация, статусы) | OK |
| 1 | Интеграционные тесты (8 сценариев) | OK |
| 2 | Dockerfile + docker-compose.yml | OK |
| 2 | Тест `/health` | OK |
| 3 | WebSocket комнаты + RoomManager | OK |
| 3 | Тесты WebSocket (7 сценариев) | OK |
| 4 | APIRouter, зависимости, роли | OK |
| 4 | Тесты ролей и доступа (7 сценариев) | OK |

---

## Контакты

Коршиков Руслан Алексеевич  
Группа ЭФБО-06-24
