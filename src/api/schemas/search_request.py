import datetime

from src.schemas import BaseScheme as BaseModel


class SearchRequest(BaseModel):
    """
    Запрос поиска сообщений

    Используется для запроса входящих сообщений.
    """

    start_date: datetime.datetime
    end_date: datetime.datetime
    limit: int
    offset: int
