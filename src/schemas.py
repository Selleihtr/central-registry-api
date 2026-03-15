import datetime
import decimal
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
    

    @pydantic.model_validator(mode='after')
    def round_all_decimals(self) -> 'BaseScheme':
        """
        Валидатор для округления Decimal полей
        """
        return round_decimal_fields(self)
    

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        # Для ответа используем формат "2024-01-01T00:00:00Z"
        json_encoders={
            datetime.datetime: utils.serialize_to_iso8601_utc
        }
    )
    

