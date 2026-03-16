import datetime
import hashlib
import json

from src.api.schemas.transactions import TransactionScheme, TransactionsData
from src.api.schemas.messages import ReceiptMessage, WrapMessage
from src.api.schemas.search_request import SearchRequest
from src.api.models import Transaction
from src.api import constants, utils, exceptions
from src import utils as ut


def incoming_service(envelope, db):
    upnacked_data = utils.unpack_envelope(envelope)
    if not upnacked_data:
        raise exceptions.BadRequestException("Empty envelope data")
    
    transactions_data = TransactionsData(**upnacked_data)
    transactions = transactions_data.transactions
    if not transactions:
        raise exceptions.BadRequestException("No transactions found")
    
    receipt_transactions = []
    saved_transactions = []
    
    for tx in transactions:
        if not tx.sign:
            raise exceptions.BadRequestException("Empty sign")
        
        if not utils.verify_transaction_hash(tx):
            raise exceptions.BadRequestException("Invalid hash")
            
        db_transaction = Transaction(**tx.model_dump())
        db.add(db_transaction)
        saved_transactions.append(db_transaction)
        
        message_data = utils.decode_base64(tx.data, as_string=True)
        if not message_data:
            raise exceptions.BadRequestException("Empty message data")
            
        wrap_message = WrapMessage(**json.loads(message_data))

        if wrap_message.info_message_type != constants.InfoMessageType.PAYMENT_RECEIPT:
            original_message_data = utils.decode_base64(wrap_message.data, as_string=True)
            original_message = json.loads(original_message_data)
            
            bank_guarantee_hash = original_message.get("BankGuaranteeHash")
            if not bank_guarantee_hash:
                raise exceptions.BadRequestException("BankGuaranteeHash not found in message")
            
            receipt_message = ReceiptMessage(
                bank_guarantee_hash=bank_guarantee_hash
            )
            
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
            
            receipt_transaction.hash = utils.calculate_transaction_hash(receipt_transaction)
            receipt_transactions.append(receipt_transaction)
    
    db.commit()
    
    for db_tx in saved_transactions:
        db.refresh(db_tx)
    
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
    if not upnacked_data:
        raise exceptions.BadRequestException("Empty envelope data")
    
    search_params = SearchRequest(**upnacked_data)
    if not search_params.start_date or not search_params.end_date:
        raise exceptions.BadRequestException("Start date and end date are required")
    
    transactions = db.query(Transaction).filter(
        Transaction.transaction_time >= search_params.start_date,
        Transaction.transaction_time <= search_params.end_date
    ).order_by(
        Transaction.transaction_time.desc()
    ).all()

    filtered = [] 
    for tx in transactions:
        try:
            wrap_message = utils.decode_base64_json(tx.data)
            wrap_message = WrapMessage(**wrap_message)
            if wrap_message.receiver_branch == "SYSTEM_A":
                tx_schema = TransactionScheme.model_validate(tx)
                filtered.append(tx_schema)
        except Exception:
            continue
    
    offset = search_params.offset or 0
    limit = search_params.limit or 10
    
    if offset >= len(filtered):
        raise exceptions.BadRequestException("Offset exceeds total count")
    
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