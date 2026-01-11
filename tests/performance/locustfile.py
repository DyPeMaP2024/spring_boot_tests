"""
Нагрузочные тесты для Spring Boot приложения с использованием Locust.

Тестирует производительность эндпоинта /endpoint при различных нагрузках.
"""
import random
import string
from locust import HttpUser, task, between, events
import yaml
from pathlib import Path


def load_config() -> dict:
    """Загружает конфигурацию из local.yaml."""
    import os
    # Путь относительно locustfile.py: tests/performance/locustfile.py -> spring-boot-tests/config/...
    config_path = Path(__file__).parent.parent.parent / "config" / "environments" / "local.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Переопределение URL для Docker окружения
    if os.getenv("APP_URL"):
        config["app"]["base_url"] = os.getenv("APP_URL")
    
    return config


def generate_token(length: int = 32) -> str:
    """Генерирует токен заданной длины из символов 0-9A-F."""
    characters = string.digits + "ABCDEF"
    return "".join(random.choice(characters) for _ in range(length))


class SpringBootUser(HttpUser):
    """
    Пользователь для нагрузочного тестирования Spring Boot приложения.
    
    Симулирует поведение пользователя:
    - LOGIN для получения доступа
    - Выполнение ACTION
    - LOGOUT для завершения сессии
    """
    wait_time = between(1, 3)  # Ожидание между запросами 1-3 секунды
    
    def on_start(self):
        """Инициализация пользователя при старте."""
        config = load_config()
        self.api_key = config["app"]["api_key"]
        self.token = generate_token(32)
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "X-Api-Key": self.api_key,
        }
        # Выполняем LOGIN при старте
        self.login()
    
    def login(self):
        """Выполняет LOGIN для получения доступа."""
        with self.client.post(
            "/endpoint",
            data={"token": self.token, "action": "LOGIN"},
            headers=self.headers,
            catch_response=True,
            name="LOGIN"
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("result") == "OK":
                        response.success()
                    else:
                        response.failure(f"LOGIN failed: {result}")
                except Exception as e:
                    response.failure(f"Invalid response: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(3)
    def perform_action(self):
        """
        Выполняет ACTION.
        
        Вес задачи: 3 (выполняется чаще, чем LOGIN/LOGOUT).
        """
        with self.client.post(
            "/endpoint",
            data={"token": self.token, "action": "ACTION"},
            headers=self.headers,
            catch_response=True,
            name="ACTION"
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("result") == "OK":
                        response.success()
                    else:
                        response.failure(f"ACTION failed: {result}")
                except Exception as e:
                    response.failure(f"Invalid response: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def logout(self):
        """
        Выполняет LOGOUT.
        
        Вес задачи: 1 (выполняется реже).
        """
        with self.client.post(
            "/endpoint",
            data={"token": self.token, "action": "LOGOUT"},
            headers=self.headers,
            catch_response=True,
            name="LOGOUT"
        ) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("result") == "OK":
                        response.success()
                        # После LOGOUT генерируем новый токен и делаем LOGIN
                        self.token = generate_token(32)
                        self.login()
                    else:
                        response.failure(f"LOGOUT failed: {result}")
                except Exception as e:
                    response.failure(f"Invalid response: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Событие при старте теста."""
    print("=" * 60)
    print("Нагрузочное тестирование Spring Boot приложения")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Событие при остановке теста."""
    print("=" * 60)
    print("Нагрузочное тестирование завершено")
    print("=" * 60)
