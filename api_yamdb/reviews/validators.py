"""Модуль с функциями-валидации."""
import re

from django.core.exceptions import ValidationError
from django.utils.timezone import now

from config import (
    URL_PROFILE_PREF, USERNAME_VALID_PATTERN,
)


def validate_not_me(username):
    """Функция-валидатор. Проверяет, что username != me."""
    if username == URL_PROFILE_PREF:
        raise ValidationError(
            f'Использовать имя "{URL_PROFILE_PREF}" в '
            f'качестве username запрещено.'
        )

    return username


def validate_username_via_regex(username):
    """Валидация поля username."""
    invalid_characters = re.sub(USERNAME_VALID_PATTERN, '', username)
    if invalid_characters:
        invalid_characters = "".join(set(invalid_characters))
        raise ValidationError(
            f'В username найдены недопустимые символы '
            f'{invalid_characters}'
        )

    return username


def validate_year(value):
    """Валидация поля year."""
    current_year = now().year
    if value > current_year:
        raise ValidationError(
            f'Нельзя добавить произведение из будущего. '
            f'{value} еще не наступил.'
            f'Сейчас {current_year} год.'
        )
    return value
