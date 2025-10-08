from typing import Any, Dict
from tqdm import tqdm

from src.agents.predictor_type_2.graphs.app.state import GraphState

from src.utils.vector_store import search_store


def node_4_search_vector_store(state: GraphState) -> Dict[str, Any]:
    print("--- 4. SEARCHING VECTOR STORE ---")
    company_id = state["input_company_id"]
    input_transactions = state["processed_input_transactions"]
    output_transactions = state["final_output_transactions"]

    output_vector_store_result = []

    for i, trx in tqdm(enumerate(input_transactions)):
        found_desc = False
        found_payee = False

        # First try to match with description:
        if trx["transaction_description"] != "":
            res = search_store(
                query=trx["transaction_description"],
                collection_name=company_id,
                k=50,
                threshold=0.85,
            )

            if res["hit"]:
                found_desc = True
                output_vector_store_result.append(res)
                output_transactions[i]["vector_found_desc"] = True

        # As a backup if desc wasnt matched / was empty try with parsed description (likely name)
        if not found_desc and trx["parsed_description"] != "":
            res = search_store(
                query=trx["parsed_description"],
                collection_name=company_id,
                k=50,
                threshold=0.5,
            )

            if res["hit"]:
                found_payee = True
                output_vector_store_result.append(res)
                output_transactions[i]["vector_found_payee"] = True

        # If neither found then append a message and a False output to vec store results (to keep length same)
        if not found_desc and not found_payee:
            output_vector_store_result.append({"hit": False, "documents": []}) # out length same
            output_transactions[i][
                "message"
            ] = "Payee/Transaction couldn't be identified in the system"

    return {
        "output_vector_store_result": output_vector_store_result,
        "final_output_transactions": output_transactions,
    }
