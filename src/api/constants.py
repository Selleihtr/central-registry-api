import enum



class HTTPCodes(enum.IntEnum):
    """HTTP статус коды"""
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

HTTP_DESCRIPTIONS = {
    200: "Успешное выполнение запроса",
    400: "Неверный запрос (отсутствуют обязательные параметры, синтаксическая ошибка)",
    404: "Ресурс не найден",
    500: "Внутренняя ошибка сервера",
}

class InfoMessageType(enum.Enum):
    GUARANTEE_ISSUE = 201
    GUARANTEE_ACCEPT = 202
    GUARANTEE_REJECT = 203
    PAYMENT_RECEIPT = 215

class TransactionType(enum.Enum):
    INFO_MESSAGE = 9      # - c информационным сообщением 
    WITH_GUARANTEE = 18   # - c гарантией


class CurrencyCodeEnum(enum.Enum):
    BYN="BYN"
    USD="USD"
    EUR="EUR"

class ObligationType(enum.Enum):
    TYPE_1 = 1
    TYPE_2 = 2 
    TYPE_3 = 3
    TYPE_4 = 4

class RevokationType(enum.Enum):
    REVOCABLE = "Отзывная"     
    IRREVOCABLE = "Безотзывная" 
