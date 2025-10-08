from typing import Any, Dict

from src.agents.predictor_type_2.graphs.app.state import GraphState


def node_5_populate_vector_data(state: GraphState) -> Dict[str, Any]:
    # populate found vector store payee details to output transaction
    print("--- 5. POPULATE VECTOR DATA INTO OUTPUT OBJECT---")

    output_transactions = state["final_output_transactions"]
    vector_store_output = state["output_vector_store_result"]

    for i, vec in enumerate(vector_store_output):
        if vec["hit"]:
            vec_metadata = vec["documents"][0]["metadata"]
            output_transactions[i]["payee"]["id"] = vec_metadata["payee_id"]
            output_transactions[i]["payee"]["name"] = vec_metadata["payee_name"]
            output_transactions[i]["payee"]["type"] = vec_metadata["payee_type"]
    
    return {"final_output_transactions": output_transactions}
