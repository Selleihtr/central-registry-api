import enum


class TransactionTypeEnum(enum.Enum):
    INFO_MESSAGE = 9      # - c информационным сообщением 
    WITH_GUARANTEE = 18   # - c гарантией


class InfoMessageTypeEnum(enum.Enum):
    OF_GUARANTEE_ISSUE = 201
    CONFIRMATION_OF_ACCEPTANCE_OF_GUARANTEE = 202
    REFUSAL_TO_ACCEPT_GUARANTEE = 203
    PAYMENT_RECEIPT = 215
