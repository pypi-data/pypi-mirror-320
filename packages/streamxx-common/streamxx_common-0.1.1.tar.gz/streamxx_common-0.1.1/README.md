# Streamxx Common

`streamxx-common` — это общий пакет утилит и вспомогательных функций для микросервисов платформы Streamxx. Пакет включает в себя функции и классы, которые можно использовать в разных сервисах, чтобы избежать дублирования кода и упростить поддержку общего функционала.

## Установка

Установите пакет через Poetry:

```bash
poetry add streamxx-common
```

Или через pip:

```bash
pip install streamxx-common
```

## Возможности

Пакет включает в себя следующие модули и функции:

- **Валидация токенов** (например, Keycloak)

## Использование

Пример использования утилиты для проверки токенов:

```python
from streamxx_common.auth.token_validator import KeycloakTokenValidator

# Инициализация валидатора
validator = KeycloakTokenValidator(
    keycloak_url="https://keycloak.example.com",
    realm_name="streamxx",
    client_id="my-client",
    client_secret="my-secret",
)

# Проверка токена
token_data = await validator.verify_token("your_jwt_token")
print(token_data)
```

## Конфигурация

Пакет поддерживает использование переменных окружения для конфигурации:

| Переменная               | Описание                  |
| ------------------------ | ------------------------- |
| `KEYCLOAK_SERVER_URL`    | URL сервера Keycloak      |
| `KEYCLOAK_REALM_NAME`    | Имя Realm в Keycloak      |
| `KEYCLOAK_CLIENT_ID`     | ID клиента в Keycloak     |
| `KEYCLOAK_CLIENT_SECRET` | Секрет клиента в Keycloak |
| `REDIS_URL`              | URL подключения к Redis   |

Пример использования переменных окружения в Docker:

```dockerfile
ENV KEYCLOAK_SERVER_URL=https://keycloak.example.com
ENV KEYCLOAK_REALM_NAME=streamxx
ENV KEYCLOAK_CLIENT_ID=my-client
ENV KEYCLOAK_CLIENT_SECRET=my-secret
```

## Запуск тестов

Для запуска тестов используйте команду:

```bash
poetry run pytest
```

Или через Docker:

```bash
docker-compose run --rm app pytest
```
