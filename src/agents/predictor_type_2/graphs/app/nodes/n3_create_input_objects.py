from typing import Any, Dict
from copy import deepcopy
from price_parser import Price

from src.agents.predictor_type_2.graphs.app.state import GraphState


def node_3_create_input_objects(state: GraphState) -> Dict[str, Any]:
    print("--- 3. TRX DESC OBJECT CREATE ---")

    df_trx = state["input_uncategorized_transactions_df"]
    predicted_column_names = state["predicted_column_names"]

    transactions = []
    transactions_out = []
    for index, row in df_trx.iterrows():
        # processed input
        str_amount = str(row[predicted_column_names["col_trx_amount"]])
        processed_amount = Price.fromstring(str_amount).amount_float

        trx_obj = {
            "id": index,
            "date": str(row[predicted_column_names["col_trx_date"]]),
            "type": str(row[predicted_column_names["col_trx_type"]]),
            "amount": processed_amount,
            "transaction_description": str(
                row[predicted_column_names["col_trx_description"]]
            ),
            "parsed_description": "",
        }
        transactions.append(trx_obj)

        # output template
        trx_out_obj = deepcopy(trx_obj)
        trx_out_obj["completed"] = False
        trx_out_obj["processed"] = False
        trx_out_obj["vector_found_desc"] = False
        trx_out_obj["vector_found_payee"] = False
        trx_out_obj["category_id"] = ""
        trx_out_obj["message"] = ""
        trx_out_obj["category_name"] = ""
        trx_out_obj["payee"] = {"id": None, "type": None, "name": None}
        trx_out_obj["receipt"] = {"type": None, "receipt_ids": [], "document_ids": []}
        transactions_out.append(trx_out_obj)

    return {
        "processed_input_transactions": transactions,
        "final_output_transactions": transactions_out,
    }
