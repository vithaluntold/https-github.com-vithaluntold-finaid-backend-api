from typing import Any, Dict, List
import json

from src.agents.predictor_type_2.chains import chain_category_predictor
from src.agents.predictor_type_2.graphs.app.state import (
    GraphState,
    TransactionOutputType,
    TxnValuesType,
    AccountCategories,
)


def predict_category_name(
    company_name: str,
    company_nature: str,
    trx: TransactionOutputType,
    predicted_trx_values: TxnValuesType,
    income_accounts: List[AccountCategories],
    expense_accounts: List[AccountCategories],
):
    account_list = None
    if trx["type"] == predicted_trx_values["type_credit"]:
        account_list = income_accounts
    elif trx["type"] == predicted_trx_values["type_debit"]:
        account_list = expense_accounts

    res = chain_category_predictor.invoke(
        input={
            "company_name": company_name,
            "company_nature": company_nature,
            "trx_desc": trx["transaction_description"],
            "trx_desc_parsed": trx["parsed_description"],
            "trx_payee": "",
            "json_categories": json.dumps(account_list),
        }
    )

    return (res["name"], res["id"])


def node_9_process_unknown_payees(state: GraphState) -> Dict[str, Any]:
    # final process on successful hits in vector store
    print("--- 9. PROCESS UNKNOWN PAYEES ---")

    input_company_name = state["input_company_name"]
    input_company_nature = state["input_company_nature"]
    income_accounts_list = state["input_income_list"]
    expense_accounts_list = state["input_expense_list"]
    output_transactions = state["final_output_transactions"]
    vector_store_output = state["output_vector_store_result"]
    pred_trx_values = state["predicted_trx_value_names"]

    for i, (vec, out_trx) in enumerate(zip(vector_store_output, output_transactions)):
        if not vec["hit"] and not out_trx["processed"]:
            
            if out_trx["transaction_description"]:
                cat_name, cat_id = "", ""

                cat_name, cat_id = predict_category_name(
                    input_company_name,
                    input_company_nature,
                    out_trx,
                    pred_trx_values,
                    income_accounts_list,
                    expense_accounts_list,
                )

                if out_trx["type"] == pred_trx_values["type_debit"]:
                    output_transactions[i]["completed"] = True
                    output_transactions[i]["processed"] = True
                    output_transactions[i]["receipt"]["type"] = "PURCHASE"
                    output_transactions[i]["category_id"] = cat_id
                    output_transactions[i]["category_name"] = cat_name

                elif out_trx["type"] == pred_trx_values["type_credit"]:
                    output_transactions[i]["completed"] = True
                    output_transactions[i]["processed"] = True
                    output_transactions[i]["receipt"]["type"] = "SALES_RECEIPT"
                    output_transactions[i]["category_id"] = cat_id
                    output_transactions[i]["category_name"] = cat_name

    return {"final_output_transactions": output_transactions}
