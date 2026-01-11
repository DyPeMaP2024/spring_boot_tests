"""
Клиент для работы с Spring Boot API.
"""
import requests
from typing import Dict, Any, Optional
from ..models.response import SuccessResponse, ErrorResponse


class ApiClient:
    """Клиент для взаимодействия с Spring Boot API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Инициализация клиента.

        Args:
            base_url: Базовый URL API
            api_key: API ключ для аутентификации
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "X-Api-Key": self.api_key,
        })

    def endpoint(
        self,
        token: str,
        action: str,
        validate_response: bool = True
    ) -> Dict[str, Any]:
        """
        Выполнить запрос к эндпоинту /endpoint.

        Args:
            token: Токен пользователя (32 символа A-Z0-9)
            action: Действие (LOGIN, ACTION, LOGOUT)
            validate_response: Валидировать ответ через Pydantic модели

        Returns:
            Словарь с ответом от API

        Raises:
            requests.RequestException: При ошибке HTTP запроса
            ValidationError: При ошибке валидации ответа (если validate_response=True)
        """
        url = f"{self.base_url}/endpoint"
        data = {
            "token": token,
            "action": action,
        }

        response = self.session.post(
            url,
            data=data,
            timeout=self.timeout
        )

        # Для тестов важно получать ответ даже при HTTP ошибках
        # Проверяем, что ответ содержит JSON
        try:
            result = response.json()
        except ValueError:
            # Если ответ не JSON, возвращаем информацию об ошибке
            return {
                "result": "ERROR",
                "message": f"HTTP {response.status_code}: {response.text[:100]}"
            }

        if validate_response:
            if result.get("result") == "OK":
                SuccessResponse(**result)
            else:
                ErrorResponse(**result)

        return result
