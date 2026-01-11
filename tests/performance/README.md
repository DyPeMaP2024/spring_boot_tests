# Нагрузочные тесты

Нагрузочное тестирование Spring Boot приложения с использованием Locust.

## Описание

Нагрузочные тесты симулируют поведение пользователей, выполняющих:
- **LOGIN** - аутентификация (вес задачи: 1)
- **ACTION** - выполнение действия (вес задачи: 3, выполняется чаще)
- **LOGOUT** - завершение сессии (вес задачи: 1)

## Установка

```bash
# Установка Locust
pip install locust

# Или через PDM
pdm install -G performance
```

## Запуск тестов

### Интерактивный режим

```bash
cd spring-boot-tests
locust -f tests/performance/locustfile.py --host=http://localhost:8080
```

Затем откройте http://localhost:8089 в браузере для управления тестами.

### Headless режим (автоматический)

```bash
cd spring-boot-tests
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8080 \
  --users=10 \
  --spawn-rate=2 \
  --run-time=60s \
  --headless \
  --html=reports/performance/locust-report.html \
  --csv=reports/performance/locust
```

### Использование скрипта

```bash
cd spring-boot-tests/tests/performance
./run_load_tests.sh
```

Параметры можно настроить через переменные окружения:
- `APP_URL` - URL приложения (по умолчанию: http://localhost:8080)
- `LOCUST_USERS` - количество пользователей (по умолчанию: 10)
- `LOCUST_SPAWN_RATE` - скорость создания пользователей/сек (по умолчанию: 2)
- `LOCUST_RUN_TIME` - время выполнения тестов (по умолчанию: 60s)
- `LOCUST_HEADLESS` - headless режим (по умолчанию: true)

## Отчеты

После выполнения тестов отчеты сохраняются в `reports/performance/`:

- **locust-report.html** - HTML отчет с графиками и статистикой
- **locust_stats.csv** - Статистика по эндпоинтам
- **locust_stats_history.csv** - История запросов во времени
- **locust_failures.csv** - Информация об ошибках
- **locust_exceptions.csv** - Исключения

### Просмотр HTML отчета

```bash
cd spring-boot-tests
xdg-open reports/performance/locust-report.html
# или
firefox reports/performance/locust-report.html
```

## Метрики

Отчеты содержат следующие метрики:

- **Request Count** - количество запросов
- **Failure Count** - количество ошибок
- **Average Response Time** - среднее время ответа
- **Min/Max Response Time** - минимальное/максимальное время ответа
- **Requests/s** - количество запросов в секунду
- **Percentiles** - процентили времени ответа (50%, 90%, 95%, 99%)

## Пример результатов

```
Type     Name          # reqs   # fails |    Avg     Min     Max
--------|------------|-------|---------|-------|-------|-------
POST     ACTION           52     0(0%) |     11       8      24
POST     LOGIN            23     0(0%) |     10       7      15
POST     LOGOUT           18     0(0%) |      4       2       6
--------|------------|-------|---------|-------|-------|-------
         Aggregated       93     0(0%) |      9       2      24
```

## Рекомендации

- Начните с небольшого количества пользователей (5-10)
- Постепенно увеличивайте нагрузку
- Мониторьте метрики приложения во время тестирования
- Используйте разные сценарии для разных типов нагрузки
