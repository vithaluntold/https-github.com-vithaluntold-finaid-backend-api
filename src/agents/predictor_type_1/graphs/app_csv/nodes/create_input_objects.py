from typing import Any, Dict

from src.agents.predictor_type_1.graphs.app_csv.state import GraphState


def node_create_input_objects(state: GraphState) -> Dict[str, Any]:
    print("--- 2. TRX DESC OBJECT CREATE ---")

    df_coa = state["input_coa_df"]
    df_trx = state["input_uncategorized_transactions_df"]
    predicted_column_names = state["predicted_column_names"]

    categories = []
    for index, row in df_coa.iterrows():
        categories.append(
            {
                "category_name": row["Account Name"],
                "category_class": row["Account Class"],
            }
        )

    transactions = []
    for index, row in df_trx.iterrows():
        transactions.append(
            {
                "id": index,
                "type": str(row[predicted_column_names["col_trx_type"]]),
                "amount": row[predicted_column_names["col_trx_amount"]],
                "transaction_description": str(
                    row[predicted_column_names["col_trx_description"]]
                ),
            }
        )

    categories_object = {"categories": categories}
    trx_desc_object = {"transactions": transactions}

    return {
        "llm_input_category_names": categories_object,
        "llm_input_transaction_descriptions": trx_desc_object,
    }
