from typing import Any, Dict

from src.agents.predictor_type_1.graphs.app_csv.state import GraphState


def node_final_cleanup(state: GraphState) -> Dict[str, Any]:
    print("--- 5. CLEANUP ---")
    
    # Cleanup predicted column names for use in sheet functions
    p_column_names = state["predicted_column_names"]
    p_column_names["col_debit"] = "Debit" if p_column_names["col_debit"] is None else p_column_names["col_debit"]
    p_column_names["col_credit"] = "Credit" if p_column_names["col_credit"] is None else p_column_names["col_credit"]
    

    return {"predicted_column_names": p_column_names}
