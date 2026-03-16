from src.api import constants

class APIException(Exception):
    """Базовый класс для исключений API"""
    def __init__(self, status_code: int, message: str = None):
        self.status_code = status_code


        self.message = message or constants.HTTP_DESCRIPTIONS.get(status_code, "Unknown error")
        super().__init__(self.message)


class BadRequestException(APIException):
    """400 - Неверный запрос"""
    def __init__(self, message: str = None):
        super().__init__(400, message or constants.HTTP_DESCRIPTIONS[400])


class NotFoundException(APIException):
    """404 - Ресурс не найден"""
    def __init__(self, message: str = None):
        super().__init__(404, message or constants.HTTP_DESCRIPTIONS[404])


class InternalServerException(APIException):
    """500 - Внутренняя ошибка сервера"""
    def __init__(self, message: str = None):
        super().__init__(500, message or constants.HTTP_DESCRIPTIONS[500])