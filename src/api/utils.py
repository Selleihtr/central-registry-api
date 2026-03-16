import hashlib
import json
import base64
import typing

from src.api.schemas.signed_api_data import SignedApiData



def unpack_envelope(
    envelope: SignedApiData,
    verify_sign: bool = True
) -> typing.Dict[str, typing.Any]:
    """
    Распаковывает конверт SignedApiData и возвращает данные и отправителя.
    
    Args:
        envelope: Объект SignedApiData с полями data, sign, signer_cert
        verify_sign: Проверять ли подпись
    
    Returns:
        Словарь с полями:
        - data: распакованные данные
        - signer: отправитель
        - sign_valid: результат проверки подписи (если verify_sign=True)
    """
    # Декодируем Data
    data_str = decode_base64(envelope.data, as_string=True)
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        data = data_str
    
    # Декодируем отправителя
    signer = decode_base64(envelope.signer_cert, as_string=True)
    
    result = {
        "data": data,
        "signer": signer
    }
    
    # Проверяем подпись
    if verify_sign:
        # expected_sign = encode_base64(
            # calculate_hash(envelope.data)
        expected_sign = create_sign_from_hash(calculate_hash(envelope.data))
        # )
        if envelope.sign != expected_sign:
            print(envelope.sign,expected_sign, sep='\n\n')
            raise ValueError(f"Invalid signature")
        result["sign_valid"] = True
    return result["data"]


def pack_envelope(
    data: typing.Any,
    signer_name: str = "SYSTEM_B"
) -> SignedApiData:
    """
    Упаковывает данные в конверт SignedApiData.
    
    Args:
        data: Данные для упаковки
        signer_name: Имя отправителя
    
    Returns:
        Объект SignedApiData с полями data, sign, signer_cert
    """
    data_base64 = encode_base64(data)
    cert_base64 = encode_base64(signer_name)
    # sign_base64 = encode_base64(calculate_hash(data_base64))
    sign_base64 = create_sign_from_hash(calculate_hash(data_base64))
    
    return SignedApiData(
        data=data_base64,
        sign=sign_base64,
        signer_cert=cert_base64
    )

def decode_base64_json(data: str) -> dict:
    """
    Декодирует Base64 строку и парсит JSON.
    Удобно для цепочки: base64 → строка → JSON
    """
    str_data = base64.b64decode(data).decode('utf-8')
    return json.loads(str_data)

def encode_base64(data: typing.Union[str, bytes, dict, list, typing.Any]) -> str:
    """
    Кодирует данные в Base64
    
    Поддерживает:
    - str: строка → UTF-8 байты → Base64
    - bytes: байты → Base64
    - dict/list: JSON → UTF-8 байты → Base64 (через to_json для dict)
    - другие типы: приводятся к строке через str()
    
    Args:
        data: Данные для кодирования
    
    Returns:
        Base64 строка (UTF-8)
    """
    # Если это словарь - используем to_json
    if isinstance(data, dict):
        data = to_json(data, sort_keys=False)
    
    # Если это строка - конвертируем в байты UTF-8
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Если это не байты - пробуем привести к строке
    if not isinstance(data, bytes):
        data = str(data).encode('utf-8')
    
    # Кодируем в Base64 и возвращаем как строку UTF-8
    return base64.b64encode(data).decode('utf-8')


def decode_base64(data: str, as_string: bool = True) -> typing.Union[str, bytes]:
    """
    Декодирует Base64 строку
    
    Args:
        data: Base64 строка
        as_string: Если True - возвращает UTF-8 строку, иначе - байты
    
    Returns:
        Декодированные данные (строка или байты)
    """
    bytes_data = base64.b64decode(data)
    if as_string:
        return bytes_data.decode('utf-8')
    return bytes_data


def to_json(data: typing.Dict, sort_keys: bool = False) -> str:
    """
    Сериализует в JSON с сохранением порядка полей
    """
    return json.dumps(
        data,
        ensure_ascii=False,      # не экранировать Unicode
        separators=(',', ':'),   # компактный формат без пробелов
        sort_keys=sort_keys      # False для сохранения порядка
    )

def calculate_hash(obj: typing.Union[typing.Dict, str, typing.Any]) -> str:
    """
    Вычисляет SHA-256 хеш для объекта или строки
    
    Args:
        obj: Объект для хеширования:
            - dict: сериализуется в JSON и хешируется
            - str: хешируется напрямую как UTF-8 строка
            - другие типы: приводятся к строке
    
    Returns:
        HEX-строка в верхнем регистре (64 символа)
    """
    if isinstance(obj, dict):
        data_for_sign = obj.copy()
        json_str = json.dumps(
            data_for_sign,
            ensure_ascii=False,
            separators=(',', ':'),
            sort_keys=False
        )
        bytes_data = json_str.encode('utf-8')
    
    elif isinstance(obj, str):
        bytes_data = obj.encode('utf-8')

    else:
        bytes_data = str(obj).encode('utf-8')

    sha256 = hashlib.sha256(bytes_data)
    return sha256.hexdigest().upper()


def create_sign_from_hash(hash_hex: str) -> str:
    """
    Взять значение Hash (HEX-строка)
    - Преобразовать в байты
    - Закодировать в Base64
    - Полученную строку использовать как значение поля Sign
    
    Args:
        hash_hex: HEX-строка хеша (например, "5F4D7E8A2C...")
    
    Returns:
        Base64 строка для поля Sign
    """
    hash_bytes = bytes.fromhex(hash_hex)
    sign_base64 = base64.b64encode(hash_bytes).decode('utf-8')
    return sign_base64


def decode_sign_to_hash(sign_b64: str) -> str:
    """
    Декодирует поле Sign (Base64) обратно в HEX-строку хеша.
    
    Args:
        sign_b64: Base64 строка из поля Sign конверта
    
    Returns:
        HEX-строка хеша в верхнем регистре (64 символа)
    
    Пример:
        sign_b64 = "NkE0NUIwOERGNTVCMjQ1MzZBRjFCMjU5RDJENkQzMjZCMjRBMkE0NzhDNDY4MkFCODAzQjM2QTk3RUYxOTM2Mw=="
        hash_hex = decode_sign_to_hash(sign_b64)  # "6A45B08DF55B24536AF1B259D2D6D326B24A2A478C4682AB803B36A97EF19363"
    """
    hash_bytes = base64.b64decode(sign_b64)
    hash_hex = hash_bytes.hex().upper()
    return hash_hex