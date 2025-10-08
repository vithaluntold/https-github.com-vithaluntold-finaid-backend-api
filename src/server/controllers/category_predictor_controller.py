import tempfile
import pandas as pd
from flask import request, Response, json, Blueprint

from src.agents.predictor_type_1 import (
    chain_category_predictor_json,
    category_predictor_app_csv,
)
from src.utils.dataframe import (
    parse_categorized_trx_dict,
    combine_cat_uncat_dfs,
    merge_cat_coa_dfs,
    create_debit_credit_cols,
    create_aggregated_df,
)

category_predictor = Blueprint("category_predictor", __name__)


@category_predictor.route("/categorize-transactions", methods=["POST"])
def handle_categorize():
    """
    request.get_json()
    - transactions:
        - id
        - type
        - amount
        - transaction_description
    - categories:
        - category_name
        - category_class
    """
    try:
        # get req.json body content
        req_data = request.get_json()
        input_categories = req_data["categories"]
        input_transactions = req_data["transactions"]

        ######################
        batch_size = 5
        output_transactions = []
        list_len = len(input_transactions)

        input_categories_str = json.dumps({"categories": input_categories})

        for i in range(0, list_len, batch_size):
            input_sublist = input_transactions[i : min(list_len, i + batch_size)]
            input_subobject = {"transactions": input_sublist}
            input_subobject_str = json.dumps(input_subobject)

            res = chain_category_predictor_json.invoke(
                input={
                    "json_trx_desc": input_subobject_str,
                    "json_categories": input_categories_str,
                }
            )

            output_transactions.extend(res["transactions"])
        ######################

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "json_categorized_trx_list": {"transactions": output_transactions},
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


@category_predictor.route("/categorize-transactions/csv", methods=["POST"])
def handle_categorize_csv():
    """
    request.files
    - file_coa
    - file_uncategorized_trx
    """
    try:
        # get files from req params
        file_coa = request.files.get("file_coa")
        file_uncategorized_trx = request.files.get("file_uncategorized_trx")

        # create tempnames
        tempfile_path_coa = tempfile.NamedTemporaryFile().name + ".csv"
        tempfile_path_uncategorized_trx = tempfile.NamedTemporaryFile().name + ".csv"

        # save files from req params
        file_coa.save(tempfile_path_coa)
        file_uncategorized_trx.save(tempfile_path_uncategorized_trx)

        ######################
        COA_CATEGORY_COL_NAME = "Account Name"

        df_coa = pd.read_csv(tempfile_path_coa)
        df_uncat_trx = pd.read_csv(tempfile_path_uncategorized_trx)

        # Predict categories
        res = category_predictor_app_csv.invoke(
            input={
                "input_coa_df": df_coa,
                "input_uncategorized_transactions_df": df_uncat_trx,
            }
        )

        # Get outputs (name of trx desc column, predicted categories json)
        p_column_names = res["predicted_column_names"]
        p_value_names_trx = res["predicted_trx_value_names"]
        p_categorized_trx_list = res["llm_output_transaction_descriptions"][
            "transactions"
        ]

        # Manipulate and merge predicted categories json with uncategorized df and chart of accounts
        df_cat_desc = parse_categorized_trx_dict(
            p_categorized_trx_list,
            p_column_names["col_trx_description"],
            COA_CATEGORY_COL_NAME,
        )
        df_cat_trx = combine_cat_uncat_dfs(
            df_cat_desc, df_uncat_trx, COA_CATEGORY_COL_NAME
        )
        df_cat_trx = merge_cat_coa_dfs(df_cat_trx, df_coa, COA_CATEGORY_COL_NAME)

        if p_column_names["type"] == 1:
            df_cat_trx = create_debit_credit_cols(
                df_cat_trx, p_column_names, p_value_names_trx
            )

        df_aggregated = create_aggregated_df(df_cat_trx, p_column_names)

        cat_csv_str = df_cat_trx.to_csv(index=False)
        agg_csv_str = df_aggregated.to_csv()  # NOTE: no index false for pivot table
        ######################

        return Response(
            response=json.dumps(
                {
                    "status": "success",
                    "csv_categorized_trx": cat_csv_str,
                    "csv_aggregated_trx": agg_csv_str,
                    "json_categorized_trx_list": p_categorized_trx_list,
                    "json_predicted_column_names": p_column_names,
                    "json_predicted_value_names_trx": p_value_names_trx,
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
