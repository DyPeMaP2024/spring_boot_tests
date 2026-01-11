#!/bin/bash
# Скрипт для запуска нагрузочных тестов Locust и генерации отчетов

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Загрузка конфигурации
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/config/environments/local.yaml"

# Параметры по умолчанию
HOST="${APP_URL:-http://localhost:8080}"
USERS="${LOCUST_USERS:-10}"
SPAWN_RATE="${LOCUST_SPAWN_RATE:-2}"
RUN_TIME="${LOCUST_RUN_TIME:-60s}"
HEADLESS="${LOCUST_HEADLESS:-true}"

echo -e "${GREEN}Запуск нагрузочных тестов Locust${NC}"
echo "Host: $HOST"
echo "Users: $USERS"
echo "Spawn rate: $SPAWN_RATE users/second"
echo "Run time: $RUN_TIME"
echo ""

# Создание директории для отчетов
REPORTS_DIR="$PROJECT_ROOT/reports/performance"
mkdir -p "$REPORTS_DIR"

# Запуск Locust в headless режиме
if [ "$HEADLESS" = "true" ]; then
    echo -e "${YELLOW}Запуск в headless режиме...${NC}"
    cd "$PROJECT_ROOT"
    locust \
        -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users="$USERS" \
        --spawn-rate="$SPAWN_RATE" \
        --run-time="$RUN_TIME" \
        --headless \
        --html="$REPORTS_DIR/locust-report.html" \
        --csv="$REPORTS_DIR/locust" \
        --loglevel=INFO
    
    echo ""
    echo -e "${GREEN}Отчеты сохранены в:${NC}"
    echo "  - HTML: $REPORTS_DIR/locust-report.html"
    echo "  - CSV: $REPORTS_DIR/locust_*.csv"
else
    echo -e "${YELLOW}Запуск в интерактивном режиме...${NC}"
    echo "Откройте http://localhost:8089 в браузере"
    cd "$PROJECT_ROOT"
    locust \
        -f tests/performance/locustfile.py \
        --host="$HOST"
fi
