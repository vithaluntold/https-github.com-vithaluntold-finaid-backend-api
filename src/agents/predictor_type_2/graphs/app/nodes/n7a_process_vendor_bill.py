from typing import Any, Dict
import pydash

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.graphs.app.utils import check_keyword


def node_7a_process_vendor_bill(state: GraphState) -> Dict[str, Any]:
    print("--- 7a. PROCESS VENDOR SINGLE BILL ---")

    input_bills = state["input_api_bills"]
    output_transactions = state["final_output_transactions"]
    pred_trx_values = state["predicted_trx_value_names"]

    for i, out_trx in enumerate(output_transactions):
        # process only payments/debits
        # for incomplete transactions
        # for vendors present in vecstore store
        if (
            out_trx["type"] == pred_trx_values["type_debit"]
            and not out_trx["processed"]
            and out_trx["payee"]["id"]
            and out_trx["payee"]["type"] == "vendor"
        ):
            # # process only if bill payments are made
            # is_bill = check_keyword(vec["documents"], "bill")
            # if is_bill:

            # get relevant data:
            cur_vendor_id = out_trx["payee"]["id"]
            cur_vendor_name = out_trx["payee"]["name"]

            cur_vendor_bills = pydash.filter_(
                input_bills, lambda b: b["payee_name"] == cur_vendor_name
            )

            # try to match bills
            matched_bills = pydash.filter_(
                cur_vendor_bills, lambda b: b["balance"] == out_trx["amount"]
            )

            # process only if a single unique bill is matched
            if len(matched_bills) == 1:
                cur_bill = matched_bills[0]

                output_transactions[i]["completed"] = True
                output_transactions[i]["processed"] = True
                output_transactions[i]["receipt"]["type"] = "BILL_PAYMENT"
                output_transactions[i]["receipt"]["receipt_ids"].append(cur_bill["id"])
                output_transactions[i]["receipt"]["document_ids"].append(cur_bill["id_document"])

            elif len(matched_bills) > 1:
                output_transactions[i]["completed"] = False
                output_transactions[i]["processed"] = True
                output_transactions[i]["message"] = "Multiple bills matched, need payment advise"

    return {"final_output_transactions": output_transactions}
