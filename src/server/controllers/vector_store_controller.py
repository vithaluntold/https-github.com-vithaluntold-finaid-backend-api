import os
import shutil
from flask import request, Response, json, Blueprint

from src.utils.vector_store import (
    convert_data_to_docs,
    index_docs,
    fetch_all_data,
    delete_store,
    VECTOR_STORE_DIR,
)

vector_store = Blueprint("vector_store", __name__)


@vector_store.route("/index-data", methods=["POST"])
def handle_index():
    """
    request.get_json()
    - company_id
    - data_list:
        - type (payee/transaction)
          payee_id
          payee_name
          payee_type (vendor/customer)
          account_id
          account_name
          account_class
          trx_type
    """
    try:
        # get req.json body content
        req_data = request.get_json()
        company_id = req_data["company_id"]
        data_list = req_data["data_list"]

        ######################
        docs = convert_data_to_docs(data_list)
        ids = index_docs(documents=docs, collection_name=company_id)
        ######################

        return Response(
            response=json.dumps({"status": "success", "stored_document_ids": ids}),
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


@vector_store.route("/get-data", methods=["GET"])
def handle_get_data():
    """
    request.args
    - company_id
    """
    try:
        # get req.json body content
        company_id = request.args.get("company_id")

        ######################
        data = fetch_all_data(collection_name=company_id)
        ######################

        return Response(
            response=json.dumps({"status": "success", "data": data}),
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


@vector_store.route("/clear-db", methods=["GET"])
def handle_clear_db():
    try:
        # get req.json body content
        company_id = request.args.get("company_id")

        ######################
        res = delete_store(collection_name=company_id)

        return Response(
            response=json.dumps(res),
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
