from typing import Any, Dict

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.chains import chain_column_selector


def node_1_column_selection(state: GraphState) -> Dict[str, Any]:
    print("--- 1. COLUMN SELECTION ---")
    trx_df = state["input_uncategorized_transactions_df"]

    # TRX DF:
    column_names = list(trx_df)
    column_names_str = ", ".join(column_names)

    res = chain_column_selector.invoke(input={"column_names_str": column_names_str})

    return {"predicted_column_names": res}
