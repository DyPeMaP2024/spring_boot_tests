# WireMock Mappings

Конфигурация моков для внешнего сервиса, от которого зависит Spring Boot приложение.

## Структура

- `mappings/` - JSON файлы с описанием моков
- `__files/` - статические файлы для ответов (если нужны)

## Доступные моки

### /auth

#### auth-success.json
- **Условие**: POST запрос с валидным токеном (32 символа hex)
- **Ответ**: HTTP 200, `{"status": "authenticated"}`
- **Использование**: Для успешной аутентификации

#### auth-error.json
- **Условие**: POST запрос с токеном, начинающимся с "INVALID"
- **Ответ**: HTTP 500, `{"error": "Authentication failed"}`
- **Использование**: Для тестирования ошибок аутентификации

#### auth-timeout.json
- **Условие**: POST запрос с токеном, начинающимся с "TIMEOUT"
- **Ответ**: HTTP 200 с задержкой 10 секунд
- **Использование**: Для тестирования таймаутов

### /doAction

#### doaction-success.json
- **Условие**: POST запрос с валидным токеном (32 символа hex)
- **Ответ**: HTTP 200, `{"status": "action_completed"}`
- **Использование**: Для успешного выполнения действия

#### doaction-error.json
- **Условие**: POST запрос с токеном, начинающимся с "ERROR"
- **Ответ**: HTTP 500, `{"error": "Action failed"}`
- **Использование**: Для тестирования ошибок выполнения действия

## Приоритеты

Моки с более высоким приоритетом (большее число) проверяются первыми. Это позволяет создавать более специфичные моки для особых случаев.

## Перезагрузка моков

После изменения моков перезапустите WireMock:

```bash
cd spring-boot-tests/docker
docker-compose -f docker-compose.test.yml restart wiremock
```

Или проверьте через API:

```bash
curl http://localhost:8888/__admin/mappings
```

## Тестирование

Проверка работы моков:

```bash
# Успешный /auth
curl -X POST http://localhost:8888/auth \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "token=0123456789ABCDEF0123456789ABCDEF"

# Успешный /doAction
curl -X POST http://localhost:8888/doAction \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "token=0123456789ABCDEF0123456789ABCDEF"
```
