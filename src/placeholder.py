import json
import sys
import os
import uuid


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.schemas.transactions import TransactionScheme
from src.api import utils
from src.api import models

transaction_placeholder = {
    "TransactionType": 9,
    "Hash": "",
    "Sign": "",
    "SignerCert": "SYSTEM_A",
    "TransactionTime": "2024-01-15T10:30:00Z",
    "MetaData": None,
    "TransactionIn": None,
    "TransactionOut": None,
}

message_placeholder = {
        "SenderBranch": "SYSTEM_B",
        "ReceiverBranch": "SYSTEM_A",
        "InfoMessageType": 201,
        "MessageTime": "2024-05-20T10:00:00Z",
        "ChainGuid": "CHAIN-001",
        "PreviousTransactionHash": None,
        "MetaData": "Первая транзакция в цепочке",
        "Data":""
    }

info_message_placeholder = {
    "InformationType": 201,
    "InformationTypeString": "Выдача гарантии",
    "Number": "BG-2024-001",
    "IssuedDate": "2024-05-20T10:00:00Z",
    "Guarantor": "ООО 'Финансовая гарантия'",
    "Beneficiary": "Государственное учреждение 'Получатель'",
    "Principal": "ООО 'Должник'",
    "Obligations": [
        {
        "Type": 1,
        "StartDate": "2024-06-01T00:00:00Z",
        "EndDate": "2024-12-01T00:00:00Z",
        "ActDate": "2024-05-15T00:00:00Z",
        "ActNumber": "ПР-2024/05/15-001",
        "Taxs": [
            {
            "Number": 1,
            "NameTax": "Обязательство по контракту №К-2024-01",
            "Amount": 50000.00,
            "PennyAmount": 0.00
            },
            {
            "Number": 2,
            "NameTax": "Гарантийное обеспечение",
            "Amount": 15000.00,
            "PennyAmount": 500.00
            }
        ]
        }
    ],
    "StartDate": "2024-06-01T00:00:00Z",
    "EndDate": "2024-12-15T00:00:00Z",
    "CurrencyCode": "USD",
    "CurrencyName": "Доллар США",
    "Amount": 65000.00,
    "RevokationInfo": "Безотзывная",
    "ClaimRightTransfer": "Не допускается",
    "PaymentPeriod": "5 рабочих дней с момента получения требования",
    "SignerName": "Иванов Иван Иванович",
    "AuthorizedPosition": "Генеральный директор",
    "BankGuaranteeHash": "5D6F8E2A1C3B9F4D7E8A2C5B1D3F6E8A9C2D4F6A8B1C3E5F7A9D2B4C6E8F0A1"
}


search_request_place_holder = {
  "StartDate": "2024-01-01T00:00:00Z",
  "EndDate": "2024-12-31T23:59:59Z",
  "Limit": 10,
  "Offset": 0
}

def create_seach_request():
    signed_api_data = dict()
    signed_api_data.setdefault("Data", utils.encode_base64(search_request_place_holder))
    signed_api_data.setdefault("SignerCert", utils.encode_base64("SYSTEM_A"))
    signed_api_data.setdefault("Sign", utils.create_sign_from_hash(utils.calculate_hash(signed_api_data["Data"])))

    return signed_api_data

def create_first_transaction():
    message_data = utils.encode_base64(info_message_placeholder)
    message_placeholder["Data"]= message_data

    transaction_data = utils.encode_base64(message_placeholder)
    signer_cert = utils.encode_base64("SYSTEM_A")
    transaction_placeholder["SignerCert"]= signer_cert
    transaction_placeholder["Sign"]=""
    transaction_placeholder["Hash"]=""
    transaction_placeholder["Data"]=transaction_data

    transaction_hash=utils.calculate_hash(transaction_placeholder)

    transaction_placeholder["Hash"]=transaction_hash
    transaction_placeholder["Sign"]=utils.create_sign_from_hash(transaction_hash)  

    signed_api_data = dict()
    signed_api_data.setdefault("Data", utils.encode_base64(transaction_placeholder))
    signed_api_data.setdefault("SignerCert", utils.encode_base64("SYSTEM_A"))
    signed_api_data.setdefault("Sign", utils.create_sign_from_hash(utils.calculate_hash(signed_api_data["Data"])))
    return signed_api_data

def create_transaction_in_db(
    db,
    signed_api_data,
    transaction_type,
    meta_data: str = None,
    transaction_in: str = None,
    transaction_out: str = None
) -> models.Transaction:
    
    data_b64 = signed_api_data["Data"]
    sign_b64 = signed_api_data["Sign"]
    cert_b64 = signed_api_data["SignerCert"] 

    data_str = utils.decode_base64(data_b64, as_string=True)
    data_dict = json.loads(data_str)
    
    tx_data = TransactionScheme(**data_dict)
    message_data = data_dict["Data"]
    
    db_transaction = models.Transaction(
        guid=uuid.uuid4().hex,
        transaction_type=transaction_type,
        data=message_data,
        hash=utils.calculate_hash(data_b64),
        sign=sign_b64,
        signer_cert=cert_b64,
        transaction_time=tx_data.transaction_time,  # 👈 уже datetime
        meta_data=meta_data,
        transaction_in=transaction_in,
        transaction_out=transaction_out
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

if __name__ == "__main__":
    print(create_first_transaction())
    print(create_seach_request())