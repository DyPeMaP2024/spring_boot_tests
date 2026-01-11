"""
Интеграционные тесты для полного цикла аутентификации и действий.

Тестирует полные сценарии работы приложения:
- LOGIN -> ACTION -> LOGOUT
- Проверка состояния токена между запросами
- Интеграция с внешним сервисом через WireMock
"""
import pytest
from src.test_framework.fixtures.token import generate_hex_token
from src.test_framework.models.response import SuccessResponse, ErrorResponse


@pytest.mark.integration
class TestAuthFlow:
    """Интеграционные тесты для полного цикла работы с токенами."""

    def test_full_cycle_login_action_logout(self, api_client):
        """
        Тест полного цикла: LOGIN -> ACTION -> LOGOUT.

        Проверяет:
        1. Успешная аутентификация через внешний сервис
        2. Выполнение действия после успешного LOGIN
        3. Завершение сессии через LOGOUT
        4. Проверка, что после LOGOUT токен больше не работает
        """
        token = generate_hex_token(32)

        # Шаг 1: LOGIN
        login_response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        assert login_response["result"] == "OK", f"LOGIN failed: {login_response}"
        SuccessResponse(**login_response)

        # Шаг 2: ACTION (должен работать после LOGIN)
        action_response = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action_response["result"] == "OK", f"ACTION failed after LOGIN: {action_response}"
        SuccessResponse(**action_response)

        # Шаг 3: LOGOUT
        logout_response = api_client.endpoint(token=token, action="LOGOUT", validate_response=False)
        assert logout_response["result"] == "OK", f"LOGOUT failed: {logout_response}"
        SuccessResponse(**logout_response)

        # Шаг 4: Проверка, что после LOGOUT ACTION больше не работает
        action_after_logout = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action_after_logout["result"] == "ERROR", "ACTION should fail after LOGOUT"
        ErrorResponse(**action_after_logout)
        assert "message" in action_after_logout

    def test_multiple_actions_after_login(self, api_client):
        """
        Тест выполнения нескольких ACTION после одного LOGIN.

        Проверяет, что токен остается активным для нескольких действий.
        """
        token = generate_hex_token(32)

        # LOGIN
        login_response = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        assert login_response["result"] == "OK"

        # Первое ACTION
        action1 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action1["result"] == "OK"

        # Второе ACTION
        action2 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action2["result"] == "OK"

        # Третье ACTION
        action3 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action3["result"] == "OK"

        # LOGOUT
        logout_response = api_client.endpoint(token=token, action="LOGOUT", validate_response=False)
        assert logout_response["result"] == "OK"

    def test_action_without_login_fails(self, api_client):
        """
        Тест, что ACTION не работает без предварительного LOGIN.

        Проверяет бизнес-логику: ACTION доступен только для залогиненных токенов.
        """
        token = generate_hex_token(32)

        # Попытка ACTION без LOGIN
        action_response = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action_response["result"] == "ERROR"
        ErrorResponse(**action_response)
        assert "message" in action_response

    def test_logout_without_login(self, api_client):
        """
        Тест LOGOUT для незалогиненных токенов.

        Проверяет поведение LOGOUT без предварительного LOGIN.
        Может вернуть OK (если токен удаляется) или ERROR (если токен не найден).
        """
        token = generate_hex_token(32)

        # LOGOUT без предварительного LOGIN
        logout_response = api_client.endpoint(token=token, action="LOGOUT", validate_response=False)
        
        # LOGOUT может вернуть OK или ERROR в зависимости от реализации
        if logout_response["result"] == "OK":
            SuccessResponse(**logout_response)
        else:
            # Если токен не найден, это тоже валидное поведение
            ErrorResponse(**logout_response)
            assert "message" in logout_response

    def test_different_tokens_independence(self, api_client):
        """
        Тест независимости разных токенов.

        Проверяет, что токены работают независимо друг от друга.
        """
        token1 = generate_hex_token(32)
        token2 = generate_hex_token(32)

        # LOGIN для token1
        login1 = api_client.endpoint(token=token1, action="LOGIN", validate_response=False)
        assert login1["result"] == "OK"

        # ACTION для token1 должен работать
        action1 = api_client.endpoint(token=token1, action="ACTION", validate_response=False)
        assert action1["result"] == "OK"

        # ACTION для token2 должен НЕ работать (не залогинен)
        action2 = api_client.endpoint(token=token2, action="ACTION", validate_response=False)
        assert action2["result"] == "ERROR"

        # LOGIN для token2
        login2 = api_client.endpoint(token=token2, action="LOGIN", validate_response=False)
        assert login2["result"] == "OK"

        # Теперь ACTION для token2 должен работать
        action2_after_login = api_client.endpoint(token=token2, action="ACTION", validate_response=False)
        assert action2_after_login["result"] == "OK"

        # token1 все еще должен работать
        action1_again = api_client.endpoint(token=token1, action="ACTION", validate_response=False)
        assert action1_again["result"] == "OK"

    def test_re_login_after_logout(self, api_client):
        """
        Тест повторного LOGIN после LOGOUT.

        Проверяет, что после LOGOUT можно снова выполнить LOGIN.
        """
        token = generate_hex_token(32)

        # Первый цикл: LOGIN -> ACTION -> LOGOUT
        login1 = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        assert login1["result"] == "OK"

        action1 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action1["result"] == "OK"

        logout1 = api_client.endpoint(token=token, action="LOGOUT", validate_response=False)
        assert logout1["result"] == "OK"

        # Второй цикл: повторный LOGIN -> ACTION -> LOGOUT
        login2 = api_client.endpoint(token=token, action="LOGIN", validate_response=False)
        assert login2["result"] == "OK"

        action2 = api_client.endpoint(token=token, action="ACTION", validate_response=False)
        assert action2["result"] == "OK"

        logout2 = api_client.endpoint(token=token, action="LOGOUT", validate_response=False)
        assert logout2["result"] == "OK"
