import json
from typing import Any, Dict

from src.agents.predictor_type_1.graphs.app_csv.state import GraphState
from src.agents.predictor_type_1.chains import chain_category_predictor_json


def node_category_prediction(state: GraphState) -> Dict[str, Any]:
    print("--- 3. TRX CATEGORY PREDICTION ---")

    categories_object = state["llm_input_category_names"]
    trx_desc_object = state["llm_input_transaction_descriptions"]

    categories_object_str = json.dumps(categories_object)
    
    batch_size = 5
    output_trx_desc_list = []
    trx_desc_list = trx_desc_object["transactions"]
    list_len = len(trx_desc_list)

    for i in range(0, list_len, batch_size):
        trx_desc_sublist = trx_desc_list[i : min(list_len, i + batch_size)]
        trx_desc_subobject = {"transactions": trx_desc_sublist}
        trx_desc_subobject_str = json.dumps(trx_desc_subobject)

        res = chain_category_predictor_json.invoke(
            input={
                "json_trx_desc": trx_desc_subobject_str,
                "json_categories": categories_object_str,
            }
        )

        output_trx_desc_list.extend(res["transactions"])

    return {
        "llm_output_transaction_descriptions": {"transactions": output_trx_desc_list}
    }
