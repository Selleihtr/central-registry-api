import datetime
import decimal
import typing

from src.api import constants
from src.schemas import BaseScheme as BaseModel


class WrapMessage(BaseModel):
    """
    Информационное сообщение
    
    Содержится в поле Data транзакции (для TransactionType = 9).
    """
    data: str # json in UTF-8 after in base64
    sender_branch: str
    receiver_branch: str
    info_message_type: constants.InfoMessageType
    message_time: datetime.datetime
    chain_guid: str
    previous_transaction_hash: typing.Optional[str] = None
    meta_data: typing.Optional[str] = None


class Tax(BaseModel):
    """ 
    Объект Tax (налог)

    Содержится в массиве поля taxs объекта Obligation
    """
    number: int 
    name_tax: str
    amount: decimal.Decimal
    penny_amount: decimal.Decimal


class Obligation(BaseModel):
    """
    Объект Obligation (обязательства)

    Содержится в поле obligations объекта GuaranteeIssueMessage (201)
    """
    type: constants.ObligationType
    start_date: datetime.datetime # только для 1 TODO
    end_date: datetime.datetime # только для 1 TODO
    act_date: datetime.datetime
    act_number: int
    taxs: list[Tax]


class GuaranteeIssueMessage(BaseModel):
    """
    Сообщение о выдаче гарантии (201)
    
    status_code:
    constants.InfoMessageType.GUARANTEE_ISSUE=201
    """
    info_message_type: constants.InfoMessageType = constants.InfoMessageType.GUARANTEE_ISSUE
    information_type_string: str
    number: str
    issued_date: datetime.datetime
    guarantor: str
    beneficiary: str
    principal: str
    obligations: list[Obligation]
    start_date: datetime.datetime
    end_date: datetime.datetime
    currency_code: constants.CurrencyCodeEnum
    currency_name: str
    amount: decimal.Decimal
    revokation_info: constants.RevokationType
    claim_right_transfer: str
    payment_period: str
    signer_name: str
    authorized_position: str
    bank_guarantee_hash: str


class GuaranteeAcceptMessage(BaseModel):
    """
    Сообщение о принятии гарантии (202)
    
    status_code:
    constants.InfoMessageType.GUARANTEE_ACCEPT=202
    """
    name: str
    bank_guarantee_hash: str
    sign: str 
    signer_cert: str


class GuaranteeRejectMessage(BaseModel):
    """
    Сообщение об отказе в принятии гарантии (203)
    
    status_code:
    constants.InfoMessageType.GUARANTEE_REJECT=203
    """
    name: str
    bank_guarantee_hash: str
    sign: str 
    signer_cert: str
    reason: str


class ReceiptMessage(BaseModel):
    """
    Квиток о получении  (215)

    status_code:
    constants.InfoMessageType.PAYMENT_RECEIPT=215
    """
    bank_guarantee_hash: str