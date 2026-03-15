import datetime

from src.api import constants
from src.schemas import BaseScheme as BaseModel



class TransactionScheme(BaseModel):   
    """ Схема для единицы хранения в реестре. 
    
    Все информационные сообщения упаковываются в транзакции.
    """          
    transaction_type: constants.TransactionTypeEnum
    data: str #base64 string
    hash: str #sha-256 ---> 64
    sign: str #base64 string
    sign_cert: str #base64 string
    transaction_time: datetime.datetime
    meta_data: str | None
    transaction_in: str | None
    transaction_out: str | None


class TransactionsData(BaseModel):
    """
    Ответ со списком транзакций
    """
    transactions: list[TransactionScheme]
    count: int