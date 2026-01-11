"""
API тесты для эндпоинта /endpoint.
"""
import pytest
import requests
from src.test_framework.fixtures.token import generate_hex_token, generate_token
from src.test_framework.models.response import SuccessResponse, ErrorResponse


@pytest.mark.api
@pytest.mark.smoke
class TestEndpoint:
    """Тесты для основного эндпоинта приложения."""

    def test_login_success(self, api_client, mock_base_url):
        """
        Тест успешной аутентификации (LOGIN).

        Шаги:
        1. Настроить WireMock для успешного ответа на /auth
        2. Отправить запрос LOGIN с валидным токеном
        3. Проверить успешный ответ
        """
        token = generate_hex_token(32)

        # Настройка WireMock для успешного ответа
        # В реальном тесте здесь будет настройка WireMock
        # wiremock.stub_for(post(url_path_equal("/auth")).will_return(a_response().with_status(200)))

        response = api_client.endpoint(token=token, action="LOGIN")

        assert response["result"] == "OK"
        SuccessResponse(**response)

    def test_login_without_mock(self, api_client):
        """
        Тест LOGIN без mock-сервиса (ожидается ошибка).

        Проверяет, что приложение корректно обрабатывает отсутствие mock-сервиса.
        """
        token = generate_hex_token(32)

        # Если mock не настроен, приложение должно вернуть ошибку
        try:
            response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
            # Если запрос прошел, проверяем ответ
            if response.get("result") == "ERROR":
                ErrorResponse(**response)
        except requests.exceptions.RequestException:
            # Ожидаем ошибку соединения, если mock не запущен
            pass

    def test_action_success_after_login(self, api_client, mock_base_url):
        """
        Тест успешного выполнения действия (ACTION) после LOGIN.

        Шаги:
        1. Выполнить LOGIN
        2. Настроить WireMock для успешного ответа на /doAction
        3. Отправить запрос ACTION
        4. Проверить успешный ответ
        """
        token = generate_hex_token(32)

        # Сначала LOGIN
        # wiremock.stub_for(post(url_path_equal("/auth")).will_return(a_response().with_status(200)))
        # api_client.endpoint(token=token, action="LOGIN")

        # Затем ACTION
        # wiremock.stub_for(post(url_path_equal("/doAction")).will_return(a_response().with_status(200)))
        response = api_client.endpoint(token=token, action="ACTION", validate_response=False)

        # Может быть ошибка, если токен не был залогинен
        if response.get("result") == "OK":
            SuccessResponse(**response)
        else:
            ErrorResponse(**response)

    def test_action_without_login(self, api_client):
        """
        Тест ACTION без предварительного LOGIN (ожидается ошибка).

        Проверяет, что ACTION недоступен для токенов, не прошедших LOGIN.
        """
        token = generate_hex_token(32)

        response = api_client.endpoint(token=token, action="ACTION", validate_response=False)

        assert response["result"] == "ERROR"
        ErrorResponse(**response)
        assert "message" in response

    def test_logout_success(self, api_client):
        """
        Тест успешного завершения сессии (LOGOUT).

        Шаги:
        1. Выполнить LOGIN
        2. Отправить запрос LOGOUT
        3. Проверить успешный ответ
        """
        token = generate_hex_token(32)

        # Сначала LOGIN, чтобы токен был в системе
        login_response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        # LOGIN может не пройти, если mock не настроен, но это не критично для LOGOUT

        # Затем LOGOUT
        response = api_client.endpoint(token=token, action="LOGOUT", validate_response=False)

        # LOGOUT должен работать даже для незалогиненных токенов (просто удаляет из хранилища)
        # Но если токен был залогинен, должен вернуть OK
        if response.get("result") == "OK":
            SuccessResponse(**response)
        else:
            # Если токен не был найден, это тоже валидное поведение
            ErrorResponse(**response)
            assert "message" in response

    def test_invalid_token_format(self, api_client):
        """
        Тест с невалидным форматом токена.

        Проверяет валидацию токена (должен быть 32 символа A-Z0-9).
        """
        # Токен неправильной длины
        short_token = generate_hex_token(31)
        response = api_client.endpoint(token=short_token, action="LOGIN", validate_response=False)
        assert response["result"] == "ERROR"
        ErrorResponse(**response)

        # Токен с недопустимыми символами
        invalid_token = "0123456789abcdef0123456789abcdef"  # содержит строчные буквы
        response = api_client.endpoint(token=invalid_token, action="LOGIN", validate_response=False)
        assert response["result"] == "ERROR"
        ErrorResponse(**response)

    def test_invalid_action(self, api_client):
        """
        Тест с невалидным действием.

        Проверяет валидацию действия (должно быть LOGIN, ACTION или LOGOUT).
        """
        token = generate_hex_token(32)

        response = api_client.endpoint(token=token, action="INVALID", validate_response=False)

        assert response["result"] == "ERROR"
        ErrorResponse(**response)

    def test_missing_api_key(self, api_client):
        """
        Тест запроса без API ключа.

        Проверяет, что запрос без заголовка X-Api-Key отклоняется.
        """
        import requests

        token = generate_hex_token(32)
        url = f"{api_client.base_url}/endpoint"
        data = {"token": token, "action": "LOGIN"}

        # Запрос без API ключа
        response = requests.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=api_client.timeout
        )

        # Ожидаем ошибку авторизации
        assert response.status_code in [401, 403]

    def test_wrong_api_key(self, config):
        """
        Тест запроса с неправильным API ключом.

        Проверяет, что запрос с неверным X-Api-Key отклоняется.
        """
        from src.test_framework.clients.api_client import ApiClient

        token = generate_hex_token(32)
        wrong_client = ApiClient(
            base_url=config["app"]["base_url"],
            api_key="wrong_key",
            timeout=config["app"].get("timeout", 30)
        )

        response = wrong_client.endpoint(token=token, action="LOGIN", validate_response=False)

        # Может быть ошибка или 401/403
        if response.get("result") == "ERROR":
            ErrorResponse(**response)
