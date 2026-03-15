import datetime
import typing
import uuid
import sqlalchemy 

from src.api import constants
from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Transaction(Base):
    """
    Единица хранения в реестре. 

    Все информационные сообщения упаковываются в транзакции.
    """
    __tablename__ = "transactions"

    guid: Mapped[str] = mapped_column(      
        sqlalchemy.String(32),              
        primary_key=True,
        default=lambda: uuid.uuid4().hex,     #hex без "-"
    )                                
    transaction_type: Mapped[constants.TransactionTypeEnum] = mapped_column(
        sqlalchemy.Enum(constants.TransactionTypeEnum),
        nullable=False,
    )
    data: Mapped[str] = mapped_column(       #base64 string
        sqlalchemy.Text,                                                       
        nullable=False,
    )                           
    hash: Mapped[str] = mapped_column(       
        sqlalchemy.String(64),               #sha-256 ---> 64
        nullable=False,
        unique=True,
    )
    sign: Mapped[str] = mapped_column(       #base64 string
        sqlalchemy.Text,   
        nullable=False,
    )
    sign_cert: Mapped[str] = mapped_column(  #base64 string
        sqlalchemy.Text,   
        nullable=False,
    )
    transaction_time: Mapped[datetime.datetime] = mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        index=True,
    )
    meta_data: Mapped[typing.Optional["str"]] = mapped_column(
        sqlalchemy.String(500),
        nullable=True,
    )
    transaction_in: Mapped[typing.Optional["str"]] = mapped_column(
        sqlalchemy.String(500),
        nullable=True,
    )   
    transaction_out: Mapped[typing.Optional["str"]] = mapped_column(
        sqlalchemy.String(500),
        nullable=True, 
    )   
    __table_args__ = (
        sqlalchemy.Index('idx_transaction_meta', 'meta_data'),  # Для поиска по meta_data
        sqlalchemy.Index('idx_transaction_time', 'transaction_time'),
    )

