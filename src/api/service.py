import json

from src.api.schemas.transactions import TransactionScheme, TransactionsData
from src.api.schemas.messages import WrapMessage
from src.api.schemas.search_request import SearchRequest
from src.api.models import Transaction
from src.api import utils


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
            tx_data = utils.decode_base64_json(tx.data)
            message_b64 = tx_data.get("Data")
            
            if message_b64:
                message = utils.decode_base64_json(message_b64)
                
                if message.get("ReceiverBranch") == "SYSTEM_A":
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
    ).model_dump()
    return response_envelope
