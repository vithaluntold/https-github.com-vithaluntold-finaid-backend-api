import pandas as pd
from operator import itemgetter
from typing import List, Dict, Tuple
from pandas import DataFrame


# Account Classes
ASSET = "Asset"
LIABILITY = "Liability"
EQUITY = "Equity"
INCOME = "Income"
EXPENSE = "Expense"


def get_constants(
    p_column_names: Dict[str, str], p_trx_value_names: Dict[str, str]
) -> Tuple[str]:
    return {
        "COL_AMOUNT": p_column_names.get("col_trx_amount"),
        "COL_DESCRIPTION": p_column_names.get("col_trx_description"),
        "COL_TYPE": p_column_names.get("col_trx_type"),
        "COL_DEBIT": p_column_names.get("col_debit"),
        "COL_CREDIT": p_column_names.get("col_credit"),
        "VAL_TYPE_DEBIT": p_trx_value_names.get("type_debit"),
        "VAL_TYPE_CREDIT": p_trx_value_names.get("type_credit"),
    }


############################# coa generation, category prediction


def parse_coa_string(coa_string: str) -> DataFrame:
    coa_list = [x.split(",") for x in coa_string.split("\n")]
    df_coa = pd.DataFrame(coa_list[1:], columns=coa_list[0])
    return df_coa


def parse_categorized_trx_dict(
    categorized_trx_list: List[Dict], desc_column_name: str, category_column_name: str
) -> DataFrame:
    """
    categorized_trx: Type:
    {
        "id": exampleID,
        "transaction_description: "example1",
        "category_name": "example_category",
        "category_pred_conf": confidence_score_number,
        "payee": "identified_payee_1"
    }
    """
    cat_trx_df = pd.DataFrame.from_dict(categorized_trx_list)
    cat_trx_df = cat_trx_df.rename(
        columns={
            "transaction_description": desc_column_name,
            "category_name": category_column_name,
        }
    )
    cat_trx_df = cat_trx_df.drop("id", axis=1)
    return cat_trx_df


def combine_cat_uncat_dfs(
    category_df: DataFrame, uncategorized_df: DataFrame, category_column_name: str
) -> DataFrame:
    df_concated = pd.concat([uncategorized_df, category_df], axis=1)
    df_concated = df_concated.loc[:, ~df_concated.columns.duplicated()]
    new_cols_order = [
        col for col in df_concated.columns if col != category_column_name
    ] + [category_column_name]
    df_concated = df_concated[new_cols_order]
    return df_concated


def merge_cat_coa_dfs(
    categorized_df: DataFrame,
    chart_of_accounts_df: DataFrame,
    category_column_name: str,
) -> DataFrame:
    return pd.merge(categorized_df, chart_of_accounts_df, on=category_column_name)


def create_debit_credit_cols(
    categorized_df: DataFrame,
    predicted_column_names: Dict[str, str],
    predicted_value_names_trx: Dict[str, str],
) -> DataFrame:
    COL_AMOUNT, COL_TYPE, COL_DEBIT, COL_CREDIT, VAL_TYPE_DEBIT, VAL_TYPE_CREDIT = (
        itemgetter(
            "COL_AMOUNT",
            "COL_TYPE",
            "COL_DEBIT",
            "COL_CREDIT",
            "VAL_TYPE_DEBIT",
            "VAL_TYPE_CREDIT",
        )(get_constants(predicted_column_names, predicted_value_names_trx))
    )
    categorized_df[COL_DEBIT] = categorized_df.apply(
        lambda row: row[COL_AMOUNT] if row[COL_TYPE] == VAL_TYPE_DEBIT else 0, axis=1
    )
    categorized_df[COL_CREDIT] = categorized_df.apply(
        lambda row: row[COL_AMOUNT] if row[COL_TYPE] == VAL_TYPE_CREDIT else 0, axis=1
    )
    return categorized_df


def create_aggregated_df(
    categorized_df_final: DataFrame,
    predicted_column_names: Dict[str, str],
) -> DataFrame:
    COL_DEBIT, COL_CREDIT = itemgetter("COL_DEBIT", "COL_CREDIT")(
        get_constants(predicted_column_names, {})
    )
    df_aggregated = categorized_df_final.pivot_table(
        index=[
            "Account Code",
            "Account Name",
            "Account Category",
            "Account Class",
            "Statement",
        ],
        values=[COL_DEBIT, COL_CREDIT],
        aggfunc="sum",
    )

    return df_aggregated


############################# financial impact, trial balance, p&l

# Aggregated df will have the following columns:
# - Account Code
# - Account Name
# - Account Category
# - Account Class
# - Statement
# - Debit
# - Credit
### - Financial Impact
# -----pl row added at the end


def clean_aggregated_df(
    df_aggregated: DataFrame,
    predicted_column_names: Dict[str, str],
) -> DataFrame:
    COL_DEBIT, COL_CREDIT = itemgetter("COL_DEBIT", "COL_CREDIT")(
        get_constants(predicted_column_names, {})
    )
    df_aggregated[COL_DEBIT] = df_aggregated[COL_DEBIT].fillna(0)
    df_aggregated[COL_CREDIT] = df_aggregated[COL_CREDIT].fillna(0)
    return df_aggregated


def create_financial_impact_column(
    df_aggregated: DataFrame,
    predicted_column_names: Dict[str, str],
) -> DataFrame:
    COL_DEBIT, COL_CREDIT = itemgetter("COL_DEBIT", "COL_CREDIT")(
        get_constants(predicted_column_names, {})
    )

    def calc_financial_impact_debit(row):
        VALUE = row[COL_DEBIT]
        if VALUE > 0:
            if row["Account Class"] == ASSET:
                return row["Financial Impact"] + VALUE
            elif row["Account Class"] == LIABILITY:
                return row["Financial Impact"] - VALUE
            elif row["Account Class"] == EQUITY:
                return row["Financial Impact"] - VALUE
            elif row["Account Class"] == INCOME:
                return row["Financial Impact"] - VALUE
            elif row["Account Class"] == EXPENSE:
                return row["Financial Impact"] - VALUE
        else:
            return row["Financial Impact"]

    def calc_financial_impact_credit(row):
        VALUE = row[COL_CREDIT]
        if VALUE > 0:
            if row["Account Class"] == ASSET:
                return row["Financial Impact"] - VALUE
            elif row["Account Class"] == LIABILITY:
                return row["Financial Impact"] + VALUE
            elif row["Account Class"] == EQUITY:
                return row["Financial Impact"] + VALUE
            elif row["Account Class"] == INCOME:
                return row["Financial Impact"] + VALUE
            elif row["Account Class"] == EXPENSE:
                return row["Financial Impact"] + VALUE
        else:
            return row["Financial Impact"]

    df_aggregated_fi = df_aggregated.copy()
    df_aggregated_fi["Financial Impact"] = 0
    df_aggregated_fi["Financial Impact"] = df_aggregated_fi.apply(
        calc_financial_impact_debit, axis=1
    )
    df_aggregated_fi["Financial Impact"] = df_aggregated_fi.apply(
        calc_financial_impact_credit, axis=1
    )
    return df_aggregated_fi


def generate_pl_data(df_aggregated_fi: DataFrame):
    df_pl = df_aggregated_fi.loc[df_aggregated_fi["Statement"] == "Profit or Loss"]
    df_pl_piv = df_pl.pivot_table(
        index=["Account Class", "Account Category", "Account Name"],
        values=["Financial Impact"],
        aggfunc="sum",
    )
    pl_total = df_pl["Financial Impact"].sum()
    return {"df_pl_piv": df_pl_piv, "total_pl": float(pl_total)}


def append_pl_row_df(df_aggregated_fi: DataFrame, total_pl: float) -> DataFrame:
    row_data = {
        "Account Code": "3200",
        "Account Name": "Profit/Loss (Current Year)",
        "Account Category": "Equity",
        "Account Class": "Equity",
        "Statement": "Balance Sheet",
        "Debit": total_pl,
        "Credit": 0,
        "Financial Impact": -total_pl,
    }
    df_aggregated_pl = df_aggregated_fi._append(row_data, ignore_index=True)
    return df_aggregated_pl


def generate_bs_data(df_aggregated_pl: DataFrame):
    df_bs = df_aggregated_pl.loc[df_aggregated_pl["Statement"] == "Balance Sheet"]
    df_bs_piv = df_bs.pivot_table(
        index=["Account Class", "Account Category", "Account Name"],
        values=["Financial Impact"],
        aggfunc="sum",
    )
    return {"df_bs_piv": df_bs_piv}


def calculate_closing_balance(
    df_opening_balance: DataFrame, df_balance_sheet: DataFrame
) -> DataFrame:
    # TODO: check columns
    df_opening_balance = df_opening_balance.sort_values(
        by=["Account Class", "Account Category", "Account Name"],
        ascending=[True, True, True],
    )
    df_balance_sheet = df_balance_sheet.sort_values(
        by=["Account Class", "Account Category", "Account Name"],
        ascending=[True, True, True],
    )
    df_closing_balance = df_balance_sheet
    df_closing_balance["Opening Balance"] = df_opening_balance["Opening Balance"]
    df_closing_balance["Closing Balance"] = (
        df_balance_sheet["Financial Impact"] + df_opening_balance["Opening Balance"]
    )
    return df_closing_balance
