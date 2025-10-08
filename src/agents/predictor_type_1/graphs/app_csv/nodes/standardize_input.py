from typing import Any, Dict
import pandas as pd

from src.agents.predictor_type_1.graphs.app_csv.state import GraphState


def node_standardize_input(state: GraphState) -> Dict[str, Any]:
    print("--- 1A. STANDARDIZE ---")

    df_trx = state["input_uncategorized_transactions_df"]
    p_column_names = state["predicted_column_names"]

    ### TODO
    df_trx[p_column_names["col_debit"]] = df_trx[p_column_names["col_debit"]].fillna(0)
    df_trx[p_column_names["col_credit"]] = df_trx[p_column_names["col_credit"]].fillna(0)

    def create_columns(row):
        if row[p_column_names["col_debit"]] > 0:
            return {
                "Transaction Type": "Debit",
                "Transaction Amount": row[p_column_names["col_debit"]],
            }
        elif row[p_column_names["col_credit"]] > 0:
            return {
                "Transaction Type": "Credit",
                "Transaction Amount": row[p_column_names["col_credit"]],
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
