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

class InfoMessageType(enum.IntEnum):
    GUARANTEE_ISSUE = 201
    GUARANTEE_ACCEPT = 202
    GUARANTEE_REJECT = 203
    PAYMENT_RECEIPT = 215

class TransactionType(enum.IntEnum):
    INFO_MESSAGE = 9      # - c информационным сообщением 
    WITH_GUARANTEE = 18   # - c гарантией


class CurrencyCodeEnum(enum.StrEnum):
    BYN="BYN"
    USD="USD"
    EUR="EUR"

class ObligationType(enum.IntEnum):
    TYPE_1 = 1
    TYPE_2 = 2 
    TYPE_3 = 3
    TYPE_4 = 4

class RevokationType(enum.StrEnum):
    REVOCABLE = "Отзывная"     
    IRREVOCABLE = "Безотзывная" 
