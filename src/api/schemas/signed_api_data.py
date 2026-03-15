from src.schemas import BaseScheme as BaseModel


class SignedApiData(BaseModel):
    """
    Конверт для всех запросов к API и ответов от API.
    
    data: JSON данные, сериализованные в UTF-8 и закодированные в Base64
    sign: ЭЦП отправителя (SHA256 от data в Base64)
    signer_cert: Сертификат открытого ключа отправителя в Base64
    """
    data: str
    sign: str
    signer_cert: str