import json
import tempfile
import pandas as pd
from flask import request, Response, json, Blueprint

from src.agents.predictor_type_2 import predictor_app

crm_predictor = Blueprint("crm_predictor", __name__)


@crm_predictor.route("/process-transactions", methods=["POST"])
def handle_process_transactions():
    """
    request.values
    - company_id

    request.files
    - file_json_bills
        - id:
        - id_document:
        - due:
        - total:
        - balance:
        - payee_id:
        - payee_name:
        - status: open/partial/closed
        - transactions: []
    - file_json_invoices
        - id:
        - id_document:
        - due:
        - total:
        - balance:
        - payee_id:
        - payee_name:
        - status: open/partial/closed
        - transactions: []
    - file_json_pa_imgs: []
    - file_csv_transactions
    """
    try:
        # get files from req params
        file_bills = request.files.get("file_json_bills")
        file_invoices = request.files.get("file_json_invoices")
        file_pa_imgs = request.files.get("file_json_pa_imgs")
        file_income_list = request.files.get("file_json_income_list")
        file_expense_list = request.files.get("file_json_expense_list")
        file_transactions = request.files.get("file_csv_transactions")
        # create tempnames
        tempfile_path_bills = tempfile.NamedTemporaryFile().name + ".json"
        tempfile_path_invoices = tempfile.NamedTemporaryFile().name + ".json"
        tempfile_path_pa_imgs = tempfile.NamedTemporaryFile().name + ".json"
        tempfile_path_income_list = tempfile.NamedTemporaryFile().name + ".json"
        tempfile_path_expense_list = tempfile.NamedTemporaryFile().name + ".json"
        tempfile_path_transactions = tempfile.NamedTemporaryFile().name + ".csv"

        # save files from req params
        file_bills.save(tempfile_path_bills)
        file_invoices.save(tempfile_path_invoices)
        file_pa_imgs.save(tempfile_path_pa_imgs)
        file_income_list.save(tempfile_path_income_list)
        file_expense_list.save(tempfile_path_expense_list)
        file_transactions.save(tempfile_path_transactions)

        # get req.json body content
        company_id = request.values["company_id"]
        company_name = request.values["company_name"]
        company_nature = request.values["company_nature"]
        company_location = request.values["company_location"]


        ######################
        with open(tempfile_path_bills) as f:
            input_bills = json.load(f)
        with open(tempfile_path_invoices) as f:
            input_invoices = json.load(f)
        with open(tempfile_path_pa_imgs) as f:
            input_pa_imgs = json.load(f)
        with open(tempfile_path_income_list) as f:
            input_income_list = json.load(f)
        with open(tempfile_path_expense_list) as f:
            input_expense_list = json.load(f)
        input_transactions_df = pd.read_csv(tempfile_path_transactions, index_col=False)

        res = predictor_app.invoke(
            {
                "input_company_id": company_id,
                "input_company_name": company_name,
                "input_company_nature": company_nature,
                "input_company_location": company_location,
                "input_income_list": input_income_list,
                "input_expense_list": input_expense_list,
                "input_uncategorized_transactions_df": input_transactions_df,
                "input_payment_advise": input_pa_imgs,
                "input_api_bills": input_bills,
                "input_api_invoices": input_invoices,
            }
        )
        output_transactions = res["final_output_transactions"]
        payment_advise = res["predicted_payment_advise"]
        ######################

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "transactions": output_transactions,
                    "payment_advise": payment_advise
                }
            ),
            status=200,
            mimetype="application/json",
        )

    except Exception as e:
        return Response(
            response=json.dumps(
                {"status": "failed", "message": str(e), "error": str(e)}
            ),
            status=500,
            mimetype="application/json",
        )
