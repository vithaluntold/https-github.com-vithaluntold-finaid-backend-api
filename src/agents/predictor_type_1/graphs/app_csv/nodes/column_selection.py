from typing import Any, Dict

from src.agents.predictor_type_1.graphs.app_csv.state import GraphState
from src.agents.predictor_type_1.chains import chain_column_selector


def node_column_selection(state: GraphState) -> Dict[str, Any]:
    print("--- 1. COLUMN SELECTION ---")
    trx_df = state["input_uncategorized_transactions_df"]

    # TRX DF:
    column_names = list(trx_df)
    column_names_str = ", ".join(column_names)

    res1 = chain_column_selector.invoke(input={"column_names_str": column_names_str})

    return {"predicted_column_names": res1}
