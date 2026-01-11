# Spring Boot Tests

Тестовый фреймворк для тестирования Spring Boot приложения на Python.

## Структура проекта

```
spring-boot-tests/
├── src/                          # Код тестовых утилит
│   └── test_framework/
│       ├── clients/              # Клиенты для Spring Boot API
│       ├── models/               # Pydantic модели
│       ├── fixtures/             # Фикстуры и утилиты
│       └── assertions/           # Кастомные проверки
├── tests/
│   ├── api/                      # API тесты
│   ├── integration/              # Интеграционные тесты
│   ├── contract/                 # Контрактные тесты
│   └── performance/              # Нагрузочные тесты
├── config/                          # Конфигурации
└── docker/                       # Docker файлы
```

## Установка

```bash
# Установка PDM (если еще не установлен)
pip install pdm

# Установка зависимостей
pdm install

# Установка тестовых зависимостей
pdm install -G test
```

## Запуск тестов

```bash
# Все тесты
pdm run pytest

# Только API тесты
pdm run pytest tests/api/

# Только smoke тесты
pdm run pytest -m smoke

# С отчетом Allure
pdm run pytest --alluredir=./allure-results
pdm run allure serve ./allure-results
```

## Конфигурация

Настройки окружений находятся в `config/environments/`:
- `local.yaml` - локальное окружение

## Отчеты

После запуска тестов отчеты сохраняются в директории `reports/`:
- `junit.xml` - JUnit XML отчет для CI/CD
- `report.html` - HTML отчет с детальной информацией

## Docker

Для запуска тестов в Docker:

```bash
cd docker
docker-compose -f docker-compose.test.yml up tests
```

## WireMock

WireMock используется для мокинга внешних сервисов. Конфигурации моков находятся в `config/wiremock/mappings/`.
