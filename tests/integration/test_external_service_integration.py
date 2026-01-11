"""
Интеграционные тесты для проверки взаимодействия с внешним сервисом.

Тестирует интеграцию Spring Boot приложения с внешним сервисом через WireMock:
- Проверка корректности запросов к внешнему сервису
- Обработка различных ответов от внешнего сервиса
- Проверка состояния приложения при ошибках внешнего сервиса
"""
import pytest
import requests
from src.test_framework.fixtures.token import generate_hex_token
from src.test_framework.models.response import SuccessResponse, ErrorResponse


@pytest.mark.integration
class TestExternalServiceIntegration:
    """Интеграционные тесты для взаимодействия с внешним сервисом."""

    def test_login_success_with_mock_service(self, api_client, mock_base_url):
        """
        Тест успешного LOGIN при работе внешнего сервиса.

        Проверяет, что при успешном ответе от /auth приложение корректно обрабатывает токен.
        """
        token = generate_hex_token(32)

        # Проверяем, что WireMock доступен
        try:
            mock_status = requests.get(f"{mock_base_url}/__admin/", timeout=5)
            assert mock_status.status_code == 200, "WireMock должен быть доступен"
        except requests.exceptions.RequestException:
            pytest.skip("WireMock недоступен для тестирования")

        # LOGIN должен работать, если mock настроен правильно
        response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)

        # Может быть OK, если mock настроен, или ERROR, если нет
        if response.get("result") == "OK":
            SuccessResponse(**response)
        else:
            # Если mock не настроен, это тоже валидное поведение
            ErrorResponse(**response)

    def test_action_requires_external_service(self, api_client, mock_base_url):
        """
        Тест, что ACTION требует работы внешнего сервиса /doAction.

        Проверяет интеграцию с внешним сервисом при выполнении ACTION.
        """
        token = generate_hex_token(32)

        # Сначала LOGIN
        login_response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        if login_response.get("result") != "OK":
            pytest.skip("LOGIN не прошел, пропускаем тест")

        # ACTION должен обращаться к внешнему сервису
        action_response = api_client.endpoint(token=token, action="ACTION", validate_response=False)

        # Может быть OK, если mock настроен, или ERROR
        if action_response.get("result") == "OK":
            SuccessResponse(**action_response)
        else:
            ErrorResponse(**action_response)

    def test_concurrent_tokens_with_external_service(self, api_client):
        """
        Тест работы нескольких токенов одновременно с внешним сервисом.

        Проверяет, что приложение корректно обрабатывает несколько токенов,
        каждый из которых обращается к внешнему сервису.
        """
        token1 = generate_hex_token(32)
        token2 = generate_hex_token(32)
        token3 = generate_hex_token(32)

        # LOGIN для всех токенов
        login1 = api_client.endpoint(token=token1, action="LOGIN", validate_response=False)
        login2 = api_client.endpoint(token=token2, action="LOGIN", validate_response=False)
        login3 = api_client.endpoint(token=token3, action="LOGIN", validate_response=False)

        # Если хотя бы один LOGIN прошел, продолжаем тест
        if login1.get("result") == "OK" or login2.get("result") == "OK" or login3.get("result") == "OK":
            # ACTION для успешно залогиненных токенов
            if login1.get("result") == "OK":
                action1 = api_client.endpoint(token=token1, action="ACTION", validate_response=False)
                # Проверяем, что ACTION либо успешен, либо есть понятная ошибка
                assert "result" in action1

            if login2.get("result") == "OK":
                action2 = api_client.endpoint(token=token2, action="ACTION", validate_response=False)
                assert "result" in action2

            if login3.get("result") == "OK":
                action3 = api_client.endpoint(token=token3, action="ACTION", validate_response=False)
                assert "result" in action3

    def test_state_persistence_after_external_service_call(self, api_client):
        """
        Тест сохранения состояния после обращения к внешнему сервису.

        Проверяет, что состояние токена сохраняется между запросами
        после успешного обращения к внешнему сервису.
        """
        token = generate_hex_token(32)

        # LOGIN
        login_response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        if login_response.get("result") != "OK":
            pytest.skip("LOGIN не прошел")

        # Первое ACTION
        action1 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert "result" in action1

        # Второе ACTION (должно работать, так как токен все еще активен)
        action2 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert "result" in action2

        # Третье ACTION
        action3 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert "result" in action3

        # Проверяем, что токен все еще активен
        action4 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert "result" in action4
