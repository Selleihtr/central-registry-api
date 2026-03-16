
import datetime
import re
import typing

def to_pascal_case(snake_str: str) -> str:
    """
    Преобразует snake_case в PascalCase
    Пример: "information_type_string" -> "InformationTypeString"
    """
    # Разбиваем по underscore и делаем каждое слово с заглавной
    words = snake_str.split('_')
    return ''.join(word.capitalize() for word in words)
def parse_iso8601_utc(value: typing.Any, field_name: str, model_class: type) -> typing.Any:
    """
    Парсит ISO 8601 строку в формате "2024-01-01T00:00:00Z" в UTC datetime.
    
    Args:
        value: Значение для парсинга
        field_name: Имя поля (для определения типа)
        model_class: Класс модели (для получения типа поля)
    
    Returns:
        datetime объект с UTC timezone или исходное значение
    """
    # Получаем тип поля
    field_type = None
    if field_name and field_name in model_class.model_fields:
        field_type = model_class.model_fields[field_name].annotation
    
    # Если поле должно быть datetime и пришла строка
    if field_type in (datetime.datetime, typing.Optional[datetime.datetime]) and isinstance(value, str):
        try:
            # Регулярка для формата YYYY-MM-DDTHH:MM:SSZ
            import re
            pattern = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z$'
            match = re.match(pattern, value)
            
            if not match:
                raise ValueError(f"Invalid ISO 8601 format: {value}")
            
            # Извлекаем компоненты даты и времени
            year, month, day, hour, minute, second = map(int, match.groups())
            
            # Создаем datetime с UTC timezone
            dt = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
            
            return dt
            
        except Exception as e:
            raise ValueError(
                f"Invalid ISO 8601 format (expected 'YYYY-MM-DDTHH:MM:SSZ'): {value}"
            ) from e
    
    return value


def serialize_to_iso8601_utc(dt: datetime.datetime) -> str:
    """
    Сериализует datetime в формат "2024-01-01T00:00:00Z"
    
    Важно: функция ожидает на вход datetime с timezone!
    """
    # Если datetime без timezone - добавляем UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    
    # Форматируем в UTC, но если время уже в UTC - оно не изменится
    dt_utc = dt.astimezone(datetime.timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")