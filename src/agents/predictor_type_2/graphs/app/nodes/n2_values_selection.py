from typing import Any, Dict

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.chains import chain_trx_values_selector


def node_2_trx_values_selection(state: GraphState) -> Dict[str, Any]:
    print("--- 2. VALUES SELECTION ---")
    trx_df = state["input_uncategorized_transactions_df"]
    p_column_names = state["predicted_column_names"]

    txr_type_values = list(trx_df[p_column_names["col_trx_type"]].unique())
    txr_type_values_str = ", ".join(txr_type_values)

    res = chain_trx_values_selector.invoke(
        input={"type_column_values_str": txr_type_values_str}
    )    

    return {"predicted_trx_value_names": res}
