from typing import Any, Dict
import pydash
from dateutil import parser

from src.agents.predictor_type_2.graphs.app.state import (
    GraphState,
    TransactionOutputType,
    BillInvoiceType,
)
from src.utils.vector_store import search_store


def transactions_filter(trx: TransactionOutputType, pa_trx_date, pa_trx_amount, payee_id, payee_name):
    # NOTE: PAYEE_ID, PAYEE_NAME UNUSED FOR NOW
    # trx_date WILL BE AHEAD pa_trx_date ALWAYS
    MAX_DATE_DIFF = 7
    
    trx_amount = float(trx["amount"])
    trx_date = parser.parse(trx["date"])

    pa_trx_amount_f = float(pa_trx_amount)
    pa_trx_date_1 = parser.parse(pa_trx_date)
    pa_trx_date_2 = parser.parse(pa_trx_date, dayfirst=True)

    if trx_amount == pa_trx_amount_f:
        if (trx_date - pa_trx_date_1).days < MAX_DATE_DIFF:
            return True
        elif (trx_date - pa_trx_date_2).days < MAX_DATE_DIFF:
            return True
        else:
            return False
    else:
        return False


def receipts_filter(receipt: BillInvoiceType, pa_rec_date, pa_rec_id):
    # NOTE: DATE UNUSED FOR NOW
    rec_id = receipt["id_document"]
    return True if rec_id == pa_rec_id else False

def create_unique_ordererd_list(receipt_ids, document_ids):
    final_receipt_ids = []
    final_document_ids = []
    
    for i, r_id, in enumerate(receipt_ids):
        if r_id not in final_receipt_ids:
            final_receipt_ids.append(r_id)
            final_document_ids.append(document_ids[i])
            
    return final_receipt_ids, final_document_ids

def find_in_vector_store(payee_vector_required, company_id):
        # try to identify required payee in vector store
        payee_id = None
        payee_name = None
        payee_type = None
        if payee_vector_required:
            res = search_store(
                query=payee_vector_required,
                collection_name=company_id,
                k=50,
                threshold=0.5,
            )
            if res["hit"]:
                vec_metadata = res["documents"][0]["metadata"]
                payee_id = vec_metadata["payee_id"]
                payee_name = vec_metadata["payee_name"]
                payee_type = vec_metadata["payee_type"]
                return (True, payee_id, payee_name, payee_type)
            else:
                return (False, None, None, None)
        else:
            return (False, None, None, None)

def node_6x_process_payment_advise(state: GraphState) -> Dict[str, Any]:
    print("--- 6X. PROCESS PAYMENT ADVISE ---")

    company_id = state["input_company_id"]
    input_bills = state["input_api_bills"]
    input_invoices = state["input_api_invoices"]
    output_transactions = state["final_output_transactions"]
    predicted_payment_advise = state["predicted_payment_advise"]

    # process each payment advise
    for payment_advise in predicted_payment_advise:
        # find if bill/invoice so we can identify vendor/customer
        is_found_payee, id_payee, name_payee, type_payee = find_in_vector_store(payment_advise["payee"], company_id)
        is_found_payer, id_payer, name_payer, type_payer = find_in_vector_store(payment_advise["payer"], company_id)

        payee_id = None
        payee_name = None
        payee_type = None
        if (is_found_payee):
            payee_id = id_payee
            payee_name = name_payee
            payee_type = type_payee         
        elif(is_found_payer):
            payee_id = id_payer
            payee_name = name_payer
            payee_type = type_payer

        # if payee is identified process payment advise esle skip
        if payee_id:
            # first find required transactions
            required_trx_indices = []
            for pa_trx in payment_advise["transaction_details"]:
                index = pydash.find_index(
                    output_transactions,
                    lambda t: transactions_filter(t, pa_trx["date"], pa_trx["amount"], payee_id, payee_name),
                )
                if index > -1:
                    required_trx_indices.append(index)

            # continue only if the required transactions are found
            if (len(required_trx_indices) > 0):

                # for vendors process bills
                if payee_type == "vendor":
                    # find required bills
                    required_bills = []
                    for pa_rec in payment_advise["receipt_details"]:
                        cur_bill = pydash.find(
                            input_bills,
                            lambda b: receipts_filter(b, pa_rec["date"], pa_rec["id"]),
                        )
                        if cur_bill:
                            required_bills.append(cur_bill)

                    # continue only if the required bills are found
                    if (len(required_bills) > 0):
                        
                        # create bills id list
                        updated_receipt_ids = [bill["id"] for bill in required_bills]
                        updated_document_ids = [bill["id_document"] for bill in required_bills]

                        # update trx indices with bill details
                        for trx_index in required_trx_indices:
                            existing_receipt_ids = output_transactions[trx_index]["receipt"]["receipt_ids"]
                            existing_document_ids = output_transactions[trx_index]["receipt"]["document_ids"]
                            existing_receipt_ids.extend(updated_receipt_ids)
                            existing_document_ids.extend(updated_document_ids)
                            
                            _receipt_ids, _document_ids = create_unique_ordererd_list(existing_receipt_ids, existing_document_ids)
                            
                            output_transactions[trx_index]["completed"] = True
                            output_transactions[trx_index]["processed"] = True
                            output_transactions[trx_index]["message"] = "Processed using payment advise"
                            output_transactions[trx_index]["receipt"]["type"] = "BILL_PAYMENT"
                            output_transactions[trx_index]["receipt"]["receipt_ids"] = _receipt_ids
                            output_transactions[trx_index]["receipt"]["document_ids"] = _document_ids

                # for customers process invoices
                elif payee_type == "customer":
                    # find required invoices
                    required_invoices = []
                    for pa_rec in payment_advise["receipt_details"]:
                        cur_invoice = pydash.find(
                            input_invoices,
                            lambda i: receipts_filter(i, pa_rec["date"], pa_rec["id"]),
                        )
                        if cur_invoice:
                            required_invoices.append(cur_invoice)

                    # continue only if the required bills are found
                    if (len(required_invoices) > 0):

                        # create invoices id list
                        updated_receipt_ids = [invoice["id"] for invoice in required_invoices]
                        updated_document_ids = [invoice["id_document"] for invoice in required_invoices]

                        # update trx indices with invoice details
                        for trx_index in required_trx_indices:
                            existing_receipt_ids = output_transactions[trx_index]["receipt"]["receipt_ids"]
                            existing_document_ids = output_transactions[trx_index]["receipt"]["document_ids"]
                            existing_receipt_ids.extend(updated_receipt_ids)
                            existing_document_ids.extend(updated_document_ids)
                            
                            _receipt_ids, _document_ids = create_unique_ordererd_list(existing_receipt_ids, existing_document_ids)

                            output_transactions[trx_index]["completed"] = True
                            output_transactions[trx_index]["processed"] = True
                            output_transactions[trx_index]["message"] = "Processed using payment advise"
                            output_transactions[trx_index]["receipt"]["type"] = "INVOICE_PAYMENT"
                            output_transactions[trx_index]["receipt"]["receipt_ids"] = _receipt_ids
                            output_transactions[trx_index]["receipt"]["document_ids"] = _document_ids
                        
            else:
                # TRXS WERENT FOUND
                pass
        else:
            # NO PAYEE ID FOUND
            pass

    return {"final_output_transactions": output_transactions}
