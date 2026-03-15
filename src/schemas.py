import datetime
import decimal
import json
import typing
import pydantic 

from src import utils


def round_decimal_fields(model: pydantic.BaseModel) -> pydantic.BaseModel:
    """
    Валидатор для автоматического округления всех Decimal полей до 2 знаков.
    Использовать с @model_validator(mode='after')
    """
    for field_name, field_value in model:
        if isinstance(field_value, decimal.Decimal):
            # Округляем до 2 знаков
            rounded = field_value.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
            setattr(model, field_name, rounded)
    return model


class BaseScheme(pydantic.BaseModel):
    """Базовый класс с парсингом ISO дат и округлением Decimal"""
    
    @pydantic.field_validator('*', mode='before')
    @classmethod
    def parse_iso8601_utc_validator(cls, value: typing.Any, info: typing.Any) -> typing.Any:
        """
        Валидатор для парсинга ISO строк в datetime
        """
        return utils.parse_iso8601_utc(value, info.field_name, cls)
    
    @pydantic.field_validator('*', mode='before')
    @classmethod
    def validate_utf8(cls, v, info):
        """
        Проверяет, что строковые поля содержат валидный UTF-8
        """
        # Если это строка - проверяем
        if isinstance(v, str):
            try:
                # Пробуем закодировать в UTF-8 и раскодировать обратно
                # Если строка содержит невалидные символы - будет ошибка
                v.encode('utf-8').decode('utf-8')
                
                # Дополнительно проверяем, что это валидный JSON (если нужно)
                # if info.field_name == 'data':  # для конкретных полей
                #     json.loads(v)
                    
            except UnicodeError as e:
                raise ValueError(f"Field {info.field_name} must be valid UTF-8: {e}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Field {info.field_name} must be valid JSON: {e}")
        
        return v

    @pydantic.model_validator(mode='after')
    def round_all_decimals(self) -> 'BaseScheme':
        """
        Валидатор для округления Decimal полей
        """
        return round_decimal_fields(self)

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        alias_generator=utils.to_pascal_case,
        populate_by_name=True,
        # Для ответа используем формат "2024-01-01T00:00:00Z"
        json_encoders={
            datetime.datetime: utils.serialize_to_iso8601_utc
        }
    )
    

