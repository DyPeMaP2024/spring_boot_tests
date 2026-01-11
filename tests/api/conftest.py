"""
Конфигурация для API тестов.
"""
import pytest
import yaml
from pathlib import Path
from src.test_framework.clients.api_client import ApiClient


def load_config() -> dict:
    """Загружает конфигурацию из local.yaml."""
    import os
    config_path = Path(__file__).parent.parent.parent / "config" / "environments" / "local.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Переопределение URL для Docker окружения
    if os.getenv("APP_URL"):
        config["app"]["base_url"] = os.getenv("APP_URL")
    if os.getenv("MOCK_URL"):
        config["mock"]["base_url"] = os.getenv("MOCK_URL")
    
    return config


@pytest.fixture(scope="session")
def config() -> dict:
    """Конфигурация тестового окружения."""
    return load_config()


@pytest.fixture(scope="session")
def api_client(config: dict) -> ApiClient:
    """Клиент для работы с Spring Boot API."""
    app_config = config["app"]
    return ApiClient(
        base_url=app_config["base_url"],
        api_key=app_config["api_key"],
        timeout=app_config.get("timeout", 30)
    )


@pytest.fixture(scope="session")
def mock_base_url(config: dict) -> str:
    """Базовый URL mock-сервиса."""
    return config["mock"]["base_url"]
