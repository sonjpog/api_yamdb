from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """
    Валидатор для проверки того, что год не из будущего.
    """
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска не может быть больше {current_year}.')
