import hashlib
import json
import enum
import base64

from typing import Any, Dict, Set, Union
from datetime import datetime
from decimal import Decimal



def encode_base64(data: Union[str, bytes, dict, list, Any]) -> str:
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


def decode_base64(data: str, as_string: bool = True) -> Union[str, bytes]:
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


def to_json(data: Dict, sort_keys: bool = False) -> str:
    """
    Сериализует в JSON с сохранением порядка полей
    """
    return json.dumps(
        data,
        ensure_ascii=False,      # не экранировать Unicode
        separators=(',', ':'),   # компактный формат без пробелов
        sort_keys=sort_keys      # False для сохранения порядка
    )

def calculate_hash(obj: Union[Dict, str, Any]) -> str:
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
    # 1. Подготавливаем байты для хеширования
    if isinstance(obj, dict):
        # Словарь: копируем и сериализуем в JSON
        data_for_sign = obj.copy()
        json_str = json.dumps(
            data_for_sign,
            ensure_ascii=False,
            separators=(',', ':'),
            sort_keys=False
        )
        bytes_data = json_str.encode('utf-8')
    
    elif isinstance(obj, str):
        # Строка: просто кодируем в UTF-8
        bytes_data = obj.encode('utf-8')
    
    else:
        # Другие типы: приводим к строке
        bytes_data = str(obj).encode('utf-8')
    
    # 2. Вычисляем SHA-256
    sha256 = hashlib.sha256(bytes_data)
    
    # 3. Возвращаем HEX в верхнем регистре
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