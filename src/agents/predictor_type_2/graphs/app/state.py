from pandas import DataFrame
from typing import Literal, TypedDict, List, Union
from src.utils.vector_store import VectorStoreType


### TYPES
class TransactionType(TypedDict):
    id: Union[str, int]
    date: str
    type: str
    amount: float
    transaction_description: str
    parsed_description: str
    parsed_type: Literal[
        "TRANSFER", "INTERNAL_TRANSFER", "CREDIT_CARD_PAYMENT", "CHECK", "UNKNOWN"
    ]


class TrxOutputPayeeType(TypedDict):
    id: int
    type: Literal["vendor", "customer"]
    name: str


class TrxOutputReceiptType(TypedDict):
    type: Literal[
        "BILL_PAYMENT",
        "BILL_ADVANCE",
        "PURCHASE",
        "VENDOR_CREDIT",
        "INVOICE_PAYMENT",
        "INVOICE_ADVANCE",
        "SALES_RECEIPT",
        "REFUND_RECEIPT",
    ]
    receipt_ids: List[Union[str, int]]
    document_ids: List[Union[str, int]]
    category_id: str
    category_name: str


class TransactionOutputType(TransactionType):
    completed: bool
    processed: bool
    vector_found_desc: bool
    vector_found_payee: bool
    message: str
    payee: TrxOutputPayeeType
    receipt: TrxOutputReceiptType


class AccountCategories:
    id: str
    name: str


class BillInvoiceType(TypedDict):
    id: str
    id_document: str
    due: str
    total: float
    balance: float
    payee_id: int
    payee_name: str
    status: Literal["open", "partial", "closed"]
    transactions: List[str]


class PaymentAdviseReceiptDetailsType(TypedDict):
    id: str
    date: str
    amount: str


class PaymentAdviseTransactionDetailsType(TypedDict):
    id: str
    date: str
    amount: str


class PaymentAdviseType(TypedDict):
    payee: str
    payer: str
    type: Literal["bill", "invoice"]
    receipt_details: List[PaymentAdviseReceiptDetailsType]
    transaction_details: List[PaymentAdviseTransactionDetailsType]


class ColumnNamesType(TypedDict):
    col_trx_date: str
    col_trx_description: str
    col_trx_amount: str
    col_trx_type: str
    col_debit: str
    col_credit: str
    type: Literal[1, 2]


class TxnValuesType(TypedDict):
    type_debit: str
    type_credit: str


class GraphState(TypedDict):
    """
    Attributes:
    ### RAW
    -   input_company_id: string used to identify vector store collection
    -   input_company_name: used for model knowledge
    -   input_company_nature: nature of company's business, used for model knowledge
    -   input_company_location: used for model knowledge
    -   input_income_list:
    -   input_expense_list
    -   input_uncategorized_transactions_df: input trx dataframe
            - id
              date
              type
              amount
              transaction_description
    -   input_api_bills:
            - id
              due
              total
              balance
              payee_id
              payee_name
              status: open/partial/closed
              transactions: [int]
    -   input_api_invoices:
            - id
              due
              total
              balance
              payee_id
              payee_name
              status: open/partial/closed
              transactions: [int]
    ### PROCESSED:
    -   processed_input_transactions:
            - id
              date
              type
              amount
              transaction_description

    ### OUTPUTS
    -   predicted_column_names: the predicted column names dictionary:
            - col_trx_date
            - col_trx_description
            - col_trx_amount
            - col_trx_type
            - col_debit
            - col_credit
            - type
    -   predicted_trx_value_names: fetches the values from the trx type field
            - type_debit
            - type_credit
    -   output_vector_store_result
            - hit
              documents:
                - score
                  metadata:
                    -  payee_id
                       payee_name
                       payee_type
                       account_id
                       account_name
                       account_class
                       trx_type

    """

    ### RAW
    input_company_id: str

    input_company_name: str

    input_company_nature: str

    input_company_location: str

    input_income_list: List[AccountCategories]

    input_expense_list: List[AccountCategories]

    input_uncategorized_transactions_df: DataFrame

    input_payment_advise: List[str]  # base64 img urls

    input_api_bills: List[BillInvoiceType]

    input_api_invoices: List[BillInvoiceType]

    ### PROCESSED:
    processed_input_transactions: List[TransactionType]

    ### OUTPUTS
    predicted_column_names: ColumnNamesType

    predicted_trx_value_names: TxnValuesType

    predicted_payment_advise: List[PaymentAdviseType]

    output_vector_store_result: List[VectorStoreType]

    final_output_transactions: List[TransactionOutputType]
