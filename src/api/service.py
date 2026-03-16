import datetime
import hashlib
import json

from src.api.schemas.transactions import TransactionScheme, TransactionsData
from src.api.schemas.messages import ReceiptMessage, WrapMessage
from src.api.schemas.search_request import SearchRequest
from src.api.models import Transaction
from src.api import constants, utils
from src import utils as ut


def incoming_service(envelope, db):
    upnacked_data = utils.unpack_envelope(envelope)
    transactions_data = TransactionsData(**upnacked_data)
    transactions = transactions_data.transactions
    
    receipt_transactions = []
    saved_transactions = []  # Сохраняем созданные SQLAlchemy объекты
    
    for tx in transactions:
        if not tx.sign:
            raise Exception("Empty sign")
        
        if not utils.verify_transaction_hash(tx):
            raise Exception("Invalid hash")
            
        db_transaction = Transaction(**tx.model_dump())
        db.add(db_transaction)
        saved_transactions.append(db_transaction)
        
        # Декодируем сообщение
        message_data = utils.decode_base64(tx.data, as_string=True)
        wrap_message = WrapMessage(**json.loads(message_data))
        
        print(f"Message type: {wrap_message.info_message_type}")

        # Если это не квиток (215) - генерируем ответный квиток
        if wrap_message.info_message_type != constants.InfoMessageType.PAYMENT_RECEIPT:
            # Получаем исходное сообщение
            original_message_data = utils.decode_base64(wrap_message.data, as_string=True)
            original_message = json.loads(original_message_data)
            
            print(f"Original message keys: {original_message.keys()}")
            
            # Извлекаем bank_guarantee_hash
            bank_guarantee_hash = original_message.get("BankGuaranteeHash")
            
            if not bank_guarantee_hash:
                raise Exception("bank_guarantee_hash not found in message")
            
            # Создаем квиток
            receipt_message = ReceiptMessage(
                bank_guarantee_hash=bank_guarantee_hash
            )
            
            # Создаем обертку для квитка с тем же chain_guid
            receipt_wrap = WrapMessage(
                data=utils.encode_base64(receipt_message.model_dump_json(by_alias=True)),
                sender_branch="SYSTEM_B",
                receiver_branch="SYSTEM_A",
                info_message_type=constants.InfoMessageType.PAYMENT_RECEIPT,
                message_time=datetime.datetime.now(datetime.timezone.utc),
                chain_guid=wrap_message.chain_guid,
                previous_transaction_hash=tx.hash,
                meta_data=None
            )
            
            # Создаем транзакцию для квитка
            receipt_transaction = TransactionScheme(
                transaction_type=9,
                data=utils.encode_base64(receipt_wrap.model_dump_json(by_alias=True)),
                hash="",
                sign="",
                signer_cert=utils.encode_base64("SYSTEM_B"),
                transaction_time=datetime.datetime.now(datetime.timezone.utc),
                meta_data=None,
                transaction_in=None,
                transaction_out=None
            )
            
            # Вычисляем хеш
            receipt_transaction.hash = utils.calculate_transaction_hash(receipt_transaction)
            
            receipt_transactions.append(receipt_transaction)
    
    db.commit()
    
    # Обновляем сохраненные SQLAlchemy объекты (если нужно)
    for db_tx in saved_transactions:
        db.refresh(db_tx)
    
    # Формируем ответ
    receipts_data = TransactionsData(
        transactions=receipt_transactions,
        count=len(receipt_transactions)
    )
    
    json_str = receipts_data.model_dump_json(by_alias=True)
    data_dict = json.loads(json_str)
    
    response_envelope = utils.pack_envelope(
        data=data_dict,
        signer_name="SYSTEM_A"
    ).model_dump(by_alias=True)
    
    return response_envelope

def outgoing_service(envelope, db):
    upnacked_data = utils.unpack_envelope(envelope)
    search_params = SearchRequest(**upnacked_data)

    transactions = db.query(Transaction).filter(
    Transaction.transaction_time >= search_params.start_date,
    Transaction.transaction_time <= search_params.end_date
    ).order_by(
        Transaction.transaction_time.desc()
    ).all()

    filtered = [] 
    for tx in transactions:  # фильтруем по SYSTEM_A 
        try:
            wrap_message = utils.decode_base64_json(tx.data)
            wrap_message = WrapMessage(**wrap_message)
            # print(wrap_message)
            if wrap_message.receiver_branch == "SYSTEM_A":
                tx_schema = TransactionScheme.model_validate(tx)
                filtered.append(tx_schema)
                    
        except Exception as e:
            print(f"Ошибка при обработке транзакции {getattr(tx, 'guid', 'unknown')}: {e}")
            continue

    offset = search_params.offset
    limit = search_params.limit
    _transactions = filtered[offset:offset + limit]
    transactions_data = TransactionsData(
        transactions=_transactions,
        count=len(filtered)  
    )

    json_str = transactions_data.model_dump_json(by_alias=True)
    data_dict = json.loads(json_str)

    response_envelope = utils.pack_envelope(
        data=data_dict,
        signer_name="SYSTEM_A"
    ).model_dump(by_alias=True)
    return response_envelope
