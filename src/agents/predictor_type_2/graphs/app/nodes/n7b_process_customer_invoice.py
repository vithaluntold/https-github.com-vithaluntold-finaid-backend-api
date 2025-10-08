from typing import Any, Dict
import pydash

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.graphs.app.utils import check_keyword


def node_7b_process_customer_invoice(state: GraphState) -> Dict[str, Any]:
    print("--- 7b. PROCESS CUSTOMER SINGLE INVOICE ---")

    input_invoices = state["input_api_invoices"]
    output_transactions = state["final_output_transactions"]
    pred_trx_values = state["predicted_trx_value_names"]

    for i, out_trx in enumerate(output_transactions):
        # process only credits/received payments
        # for incomplete transactions
        # for customers present in vecstore store
        if (
            out_trx["type"] == pred_trx_values["type_credit"]
            and not out_trx["processed"]
            and out_trx["payee"]["id"]
            and out_trx["payee"]["type"] == "customer"
        ):
            # # process only if invoice payments are made
            # is_invoice = check_keyword(vec["documents"], "invoice")
            # if is_invoice:

            # get relevant data:
            cur_customer_id = out_trx["payee"]["id"]
            cur_customer_name = out_trx["payee"]["name"]
            cur_customer_invoices = pydash.filter_(
                input_invoices, lambda b: b["payee_name"] == cur_customer_name
            )

            # try to match invoices
            matched_invoices = pydash.filter_(
                cur_customer_invoices, lambda b: b["balance"] == out_trx["amount"]
            )

            # process only if a single unique invoice is matched
            if len(matched_invoices) == 1:
                cur_invoice = matched_invoices[0]

                output_transactions[i]["completed"] = True
                output_transactions[i]["processed"] = True
                output_transactions[i]["receipt"]["type"] = "INVOICE_PAYMENT"
                output_transactions[i]["receipt"]["receipt_ids"].append(cur_invoice["id"])
                output_transactions[i]["receipt"]["document_ids"].append(cur_invoice["id_document"])

            elif len(matched_invoices) > 1:
                output_transactions[i]["completed"] = False
                output_transactions[i]["processed"] = True
                output_transactions[i]["message"] = "Multiple invoices matched, need payment advise"

    return {"final_output_transactions": output_transactions}
