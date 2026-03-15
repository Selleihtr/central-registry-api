
import datetime
import typing


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
            # Проверяем, что строка соответствует ожидаемому формату
            if not value.endswith('Z'):
                raise ValueError(f"Expected ISO format with Z, got: {value}")
            
            # Убираем Z и парсим
            dt_str = value[:-1]  # убираем Z
            dt = datetime.datetime.fromisoformat(dt_str)
            
            # Добавляем UTC timezone
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            
            return dt
        except ValueError as e:
            raise ValueError(
                f"Invalid ISO 8601 format (expected 'YYYY-MM-DDTHH:MM:SSZ'): {value}"
            ) from e
    
    return value


def serialize_to_iso8601_utc(dt: datetime.datetime) -> str:
    """
    Сериализует datetime в формат "2024-01-01T00:00:00Z"
    """
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
