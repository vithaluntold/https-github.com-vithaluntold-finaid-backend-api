from typing import Any, Dict

from src.agents.predictor_type_2.graphs.app.state import GraphState


def node_6_process_vc_initial(state: GraphState) -> Dict[str, Any]:
    # initial process on successful hits in vector store
    print("--- 6. PROCESS VENDOR CUSTOMER INITIAL ---")

    output_transactions = state["final_output_transactions"]
    pred_trx_values = state["predicted_trx_value_names"]

    for i, out_trx in enumerate(output_transactions):
        # TODO this may not account for vector_found_desc
        if out_trx["vector_found_payee"] and not out_trx["processed"]:

            # check vendors present in vector store
            if out_trx["payee"]["type"] == "vendor" and out_trx["payee"]["id"]:

                # check if vendor credit trx
                if out_trx["type"] == pred_trx_values["type_credit"]:
                    output_transactions[i]["completed"] = True
                    output_transactions[i]["processed"] = True
                    output_transactions[i]["receipt"]["type"] = "VENDOR_CREDIT"

            # check customers present in vector store
            if out_trx["payee"]["type"] == "customer" and out_trx["payee"]["id"]:

                # check if customer refund trx
                if out_trx["type"] == pred_trx_values["type_debit"]:
                    output_transactions[i]["completed"] = True
                    output_transactions[i]["processed"] = True
                    output_transactions[i]["receipt"]["type"] = "REFUND_RECEIPT"

    return {"final_output_transactions": output_transactions}
