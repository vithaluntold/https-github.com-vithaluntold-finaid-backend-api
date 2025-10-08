import tempfile
import pandas as pd
from flask import request, Response, json, Blueprint

from src.agents.coa_generator import (
    chain_coa_generator_csv,
    chain_coa_generator_desc,
)

coa_generator = Blueprint("coa_generator", __name__)


@coa_generator.route("/generate-csv", methods=["POST"])
def handle_generate_csv():
    """
    request.files
    - file_categories
    """
    try:
        # get files from req params
        file_categories = request.files.get("file_categories")

        # create tempnames
        tempfile_path_categories = tempfile.NamedTemporaryFile().name + ".csv"

        # save files from req params
        file_categories.save(tempfile_path_categories)

        ######################
        df_coa_input = pd.read_csv(tempfile_path_categories)
        str_coa_input = df_coa_input.to_csv(index=False)

        coa_string = chain_coa_generator_csv.invoke(input={"csv_data": str_coa_input})
        ######################

        return Response(
            response=json.dumps({"status": "success", "csv_coa": coa_string}),
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


@coa_generator.route("/generate-desc", methods=["POST"])
def handle_generate_desc():
    """
    request.get_json()
    - desc_business
    - desc_industry
    - desc_revenue_sources
    - desc_primary_expenses
    - desc_departments
    - desc_standards
    - desc_compliance
    - desc_country
    """
    try:
        # get req.json body content
        req_data = request.get_json()
        desc_business = req_data["desc_business"]
        desc_industry = req_data["desc_industry"]
        desc_revenue_sources = req_data["desc_revenue_sources"]
        desc_primary_expenses = req_data["desc_primary_expenses"]
        desc_departments = req_data["desc_departments"]
        desc_standards = req_data["desc_standards"]
        desc_compliance = req_data["desc_compliance"]
        desc_country = req_data["desc_country"]

        ######################
        coa_string = chain_coa_generator_desc.invoke(
            input={
                "desc_business": desc_business,
                "desc_industry": desc_industry,
                "desc_revenue_sources": desc_revenue_sources,
                "desc_primary_expenses": desc_primary_expenses,
                "desc_departments": desc_departments,
                "desc_standards": desc_standards,
                "desc_compliance": desc_compliance,
                "desc_country": desc_country,
            }
        )
        ######################

        return Response(
            response=json.dumps({"status": "success", "csv_coa": coa_string}),
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
