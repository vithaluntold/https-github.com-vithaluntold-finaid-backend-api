from pandas import DataFrame
from typing import Literal, TypedDict, List, Dict, Union


class GraphState(TypedDict):
    """
    Attributes:
    -   input_coa_df: input coa dataframe
    -   input_uncategorized_transactions_df: input trx dataframe
    -   predicted_column_names: the predicted column names dictionary:
            - col_trx_amount
            - col_trx_description
            - col_trx_type
            - col_debit
            - col_credit
            - type
    -   predicted_trx_value_names: fetches the values from the trx type field
            - val_debit
            - val_credit
    -   llm_input_category_names: Object containing category names and their classes
    -   llm_input_transaction_descriptions: Object containing input transaction ids, descriptions, amount and type
    -   llm_output_transaction_descriptions: Object similar to input transactions, with category_name, category_pred_conf, payee fields added
    """

    input_coa_df: DataFrame

    input_uncategorized_transactions_df: DataFrame
    
    predicted_column_names: Dict[str, str]
    
    predicted_trx_value_names: Dict[str, str]
    
    llm_input_category_names:  Dict[
        Literal["categories"],
        List[Dict[Literal["category_name", "category_class"], str]],
    ]

    llm_input_transaction_descriptions: Dict[
        Literal["transactions"],
        List[Dict[Literal["id", "transaction_description", "type", "amount"], str]],
    ]

    llm_output_transaction_descriptions: Dict[
        Literal["transactions"],
        List[Dict[Literal["id", "transaction_description", "category_name", "category_pred_conf", "payee"], str]],
    ]
