from typing import Any, Dict
import pandas as pd
from price_parser import Price

from src.agents.predictor_type_2.graphs.app.state import GraphState


def node_1a_standardize_input(state: GraphState) -> Dict[str, Any]:
    print("--- 1A. STANDARDIZE ---")

    df_trx = state["input_uncategorized_transactions_df"]
    p_column_names = state["predicted_column_names"]

    ### TODO
    df_trx[p_column_names["col_debit"]] = df_trx[p_column_names["col_debit"]].fillna(0)
    df_trx[p_column_names["col_credit"]] = df_trx[p_column_names["col_credit"]].fillna(0)

    def create_columns(row):
        val_debit_str = str(row[p_column_names["col_debit"]])
        val_credit_str = str(row[p_column_names["col_credit"]])
        val_debit_processed = Price.fromstring(val_debit_str).amount_float
        val_credit_processed = Price.fromstring(val_credit_str).amount_float
        
        
        if val_debit_processed > 0:
            return {
                "Transaction Type": "Debit",
                "Transaction Amount": val_debit_processed,
            }
        elif val_credit_processed > 0:
            return {
                "Transaction Type": "Credit",
                "Transaction Amount": val_credit_processed,
            }

    df_trx[["Transaction Type", "Transaction Amount"]] = df_trx.apply(
        create_columns, axis=1, result_type="expand"
    )
    ###
    p_column_names["col_trx_amount"] = "Transaction Amount"
    p_column_names["col_trx_type"] = "Transaction Type"

    return {
        "input_uncategorized_transactions_df": df_trx,
        "predicted_column_names": p_column_names,
    }
