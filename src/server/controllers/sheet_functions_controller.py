import tempfile
import pandas as pd
from io import StringIO
from flask import request, Response, json, Blueprint

from src.utils.dataframe import (
    clean_aggregated_df,
    create_financial_impact_column,
    generate_pl_data,
    append_pl_row_df,
    generate_bs_data,
    calculate_closing_balance,
)

sheet_functions = Blueprint("sheet_functions", __name__)


@sheet_functions.route("/generate-financial-impact", methods=["POST"])
def handle_generate_financial_impact():
    """
    request.get_json()
    - csv_aggregated_str
    - predicted_column_names
    """
    try:
        # get req.json body content
        req_data = request.get_json()
        csv_aggregated_str = req_data['csv_aggregated_str']
        p_column_names = req_data['predicted_column_names']

        ######################
        df_aggregated = pd.read_csv(StringIO(csv_aggregated_str))
        df_aggregated = clean_aggregated_df(df_aggregated, p_column_names)
        df_aggregated_fi = create_financial_impact_column(df_aggregated, p_column_names)

        csv_aggregated_fi_string = df_aggregated_fi.to_csv(index=False)
        ######################

        return Response(
            response=json.dumps(
                {"status": "success", "csv_aggregated_fi": csv_aggregated_fi_string}
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


@sheet_functions.route("/generate-pl", methods=["POST"])
def handle_generate_profit_loss():
    """
    request.files
    - file_aggregated_fi
    """
    try:
        # get files from req params
        file_aggregated_fi = request.files.get("file_aggregated_fi")

        # create tempnames
        tempfile_path_aggregated_fi = tempfile.NamedTemporaryFile().name + ".csv"

        # save files from req params
        file_aggregated_fi.save(tempfile_path_aggregated_fi)

        ######################
        df_aggregated_fi = pd.read_csv(tempfile_path_aggregated_fi)

        # generate pl data
        pl_data = generate_pl_data(df_aggregated_fi)
        total_pl = pl_data["total_pl"]
        df_pl_piv = pl_data["df_pl_piv"]

        # append PL to aggregated data
        df_aggregated_pl = append_pl_row_df(df_aggregated_fi, total_pl)

        csv_pl_piv = df_pl_piv.to_csv() # NOTE: no index false for pivot table
        csv_aggregated_pl_string = df_aggregated_pl.to_csv(index=False)
        ######################

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "total_pl": total_pl,
                    "csv_pl_piv": csv_pl_piv,
                    "csv_aggregated_pl": csv_aggregated_pl_string,
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


@sheet_functions.route("/generate-bs", methods=["POST"])
def handle_generate_balance_sheet():
    """
    request.files
    - file_aggregated_pl
    """
    try:
        # get files from req params
        file_aggregated_pl = request.files.get("file_aggregated_pl")

        # create tempnames
        tempfile_path_aggregated_pl = tempfile.NamedTemporaryFile().name + ".csv"

        # save files from req params
        file_aggregated_pl.save(tempfile_path_aggregated_pl)

        ######################
        # generate balance sheet data
        df_aggregated_pl = pd.read_csv(tempfile_path_aggregated_pl)
        bs_data = generate_bs_data(df_aggregated_pl)
        df_bs_piv = bs_data["df_bs_piv"]

        csv_bs_piv = df_bs_piv.to_csv() # NOTE: no index false for pivot table
        ######################

        return Response(
            response=json.dumps({"status": "success", "csv_bs_piv": csv_bs_piv}),
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


@sheet_functions.route("/calc-closing-balance", methods=["POST"])
def handle_calculate_closing_balance():
    """
    request.files
    - file_balance_sheet
    - file_opening_balance
    """
    try:
        # get files from req params
        file_balance_sheet = request.files.get("file_balance_sheet")
        file_opening_balance = request.files.get("file_opening_balance")

        # create tempnames
        tempfile_path_balance_sheet = tempfile.NamedTemporaryFile().name + ".csv"
        tempfile_path_opening_balance = tempfile.NamedTemporaryFile().name + ".csv"

        # save files from req params
        file_balance_sheet.save(tempfile_path_balance_sheet)
        file_opening_balance.save(tempfile_path_opening_balance)

        ######################
        # generate balance sheet data
        df_balance_sheet = pd.read_csv(tempfile_path_balance_sheet)
        df_opening_balance = pd.read_csv(tempfile_path_opening_balance)
        df_closing_balance = calculate_closing_balance(
            df_opening_balance=df_opening_balance, df_balance_sheet=df_balance_sheet
        )

        csv_closing_balance = df_closing_balance.to_csv()
        ######################

        return Response(
            response=json.dumps(
                {"status": "success", "csv_closing_balance": csv_closing_balance}
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
