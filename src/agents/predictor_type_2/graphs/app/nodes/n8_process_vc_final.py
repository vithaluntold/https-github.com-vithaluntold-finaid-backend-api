from typing import Any, Dict, List
import json

from src.agents.predictor_type_2.chains import chain_category_predictor
from src.agents.predictor_type_2.graphs.app.state import (
    GraphState,
    TransactionOutputType,
    TxnValuesType,
    AccountCategories,
)
from src.agents.predictor_type_2.graphs.app.utils import (
    check_keyword,
    check_common_category,
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
            "trx_payee": trx["payee"]["name"],
            "json_categories": json.dumps(account_list),
        }
    )

    return (res["name"], res["id"])


def node_8_process_vc_final(state: GraphState) -> Dict[str, Any]:
    # final process on successful hits in vector store
    print("--- 8. PROCESS VENDOR CUSTOMER FINAL ---")

    input_company_name = state["input_company_name"]
    input_company_nature = state["input_company_nature"]
    income_accounts_list = state["input_income_list"]
    expense_accounts_list = state["input_expense_list"]
    output_transactions = state["final_output_transactions"]
    vector_store_output = state["output_vector_store_result"]
    pred_trx_values = state["predicted_trx_value_names"]

    for i, (vec, out_trx) in enumerate(zip(vector_store_output, output_transactions)):
        if vec["hit"] and not out_trx["processed"]:

            # Process for items where vector was found via payee or description (logic should work for both?)
            if out_trx["vector_found_payee"] or out_trx["vector_found_desc"]:
                # NOTE payee_id/name might be empty
                
                # check vendors present in vector store
                if out_trx["payee"]["type"] == "vendor":
                    # check expense or bill, process expense
                    is_bill = check_keyword(vec["documents"], "bill")

                    if not is_bill:
                        cat_name, cat_id = "", ""
                        cat_name, cat_id = check_common_category(vec["documents"])
                        if cat_id == "":
                            cat_name, cat_id = predict_category_name(
                                input_company_name,
                                input_company_nature,
                                out_trx,
                                pred_trx_values,
                                income_accounts_list,
                                expense_accounts_list,
                            )
                        output_transactions[i]["completed"] = True
                        output_transactions[i]["processed"] = True
                        output_transactions[i]["receipt"]["type"] = "PURCHASE"
                        output_transactions[i]["category_id"] = cat_id
                        output_transactions[i]["category_name"] = cat_name
                    else:
                        output_transactions[i]["completed"] = True
                        output_transactions[i]["processed"] = True
                        output_transactions[i]["receipt"]["type"] = "BILL_ADVANCE"

                # check customers present in vector store
                elif out_trx["payee"]["type"] == "customer":
                    # check invoice or sales, process sales
                    is_invoice = check_keyword(vec["documents"], "invoice")

                    if not is_invoice:
                        cat_name, cat_id = "", ""
                        cat_name, cat_id = check_common_category(vec["documents"])
                        if cat_id == "":
                            cat_name, cat_id = predict_category_name(
                                input_company_name,
                                input_company_nature,
                                out_trx,
                                pred_trx_values,
                                income_accounts_list,
                                expense_accounts_list,
                            )
                        output_transactions[i]["completed"] = True
                        output_transactions[i]["processed"] = True
                        output_transactions[i]["receipt"]["type"] = "SALES_RECEIPT"
                        output_transactions[i]["category_id"] = cat_id
                        output_transactions[i]["category_name"] = cat_name
                    else:
                        output_transactions[i]["completed"] = True
                        output_transactions[i]["processed"] = True
                        output_transactions[i]["receipt"]["type"] = "INVOICE_ADVANCE"

    return {"final_output_transactions": output_transactions}
