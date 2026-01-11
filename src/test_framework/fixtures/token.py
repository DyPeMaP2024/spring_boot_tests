"""
Утилиты для генерации токенов.
"""
import random
import string


def generate_token(length: int = 32) -> str:
    """
    Генерирует токен заданной длины из символов A-Z0-9.

    Args:
        length: Длина токена (по умолчанию 32)

    Returns:
        Сгенерированный токен
    """
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_hex_token(length: int = 32) -> str:
    """
    Генерирует токен в hex формате (0-9A-F).

    Args:
        length: Длина токена (по умолчанию 32)

    Returns:
        Сгенерированный токен в hex формате
    """
    characters = string.digits + "ABCDEF"
    return "".join(random.choice(characters) for _ in range(length))
