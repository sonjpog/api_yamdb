import re

from django.core.exceptions import ValidationError
from django.utils import timezone

from .constants import REGULAR_CHECK_LOGIN_VALID, USERNAME_ME


def validate_year(value):
    """Валидатор для проверки того, что год не из будущего."""

    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска не может быть больше {current_year}.')


def validate_username(username):
    if username == USERNAME_ME:
        raise ValidationError(
            'Зарезервированный логин, нельзя использовать'
        )
    if not re.match(REGULAR_CHECK_LOGIN_VALID, username):
        raise ValidationError(
            'В логине нельзя использовать символы, отличные от букв'
            'в верхнем и нижнем регистрах, цифр, знаков подчеркивания,'
            'точки, знаков плюса, минуса и собаки (@)'
        )
    return username
