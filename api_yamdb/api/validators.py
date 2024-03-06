from rest_framework.validators import ValidationError
from datetime import datetime as dt


def year_validate(year) -> bool:
    """Валидация года."""

    if year > dt.now().year:
        raise ValidationError('Проекты из будущего не добавляем')
