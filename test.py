from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from pprint import pprint as print
import json

# from src.agents.coa_generator.chains import (
#     chain_coa_generator_csv,
#     chain_coa_generator_desc,
# )

# # from src.agents.category_predictor.chains import chain_column_selector
# # from src.agents.category_predictor import category_predictor_app
# from src.utils.dataframe import parse_coa_string
# from src.agents.predictor_type_2 import predictor_app

# from src.agents.predictor_type_2.chains import (
#     chain_category_predictor,
#     chain_description_parser,
# )
# from src.utils.category_data import get_categories

from src.utils.vector_store import search_store, get_vector_store_debug


if __name__ == "__main__":
    INPUT_CATEGORY_NAMES = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\1-category_names.csv"
    INPUT_UNCATEGORIZED_TRX = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\2-uncategorized_transactions.csv"
    INPUT_COA = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\OUTPUT_coa.csv"
    OUTPUT_CAT_TRX_PATH = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\output.csv"
    INPUT_T2_UNCAT_TRX = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\type2_transactions.csv"
    INPUT_T2_BILLS = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\type2_input_bills.json"
    INPUT_T2_INVOICES = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\type2_input_invoices.json"
    INPUT_IMGS = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\finaid-agents-backend\\.TEST_INPUT\\images\\type2_pa_imgs.json"
    INPUT_T3_UNCAT_TRX = "C:\\Users\\nimish\\Programs\\Work\\GarageUni\\Finace\\finaid-agents-backend\\.TEST_INPUT\\trx_chase_TEST.csv"

    #################
    # df_coa_input = pd.read_csv(INPUT_CATEGORY_NAMES)
    # str_coa_input = df_coa_input.to_csv(index=False)

    # coa_string = chain_coa_generator_csv.invoke(input={"csv_data": str_coa_input})
    # coa_string = chain_coa_generator_desc.invoke(input={
    #     "desc_business": "LLC",
    #     "desc_industry": "Retail",
    #     "desc_revenue_sources": "Product Sales",
    #     "desc_primary_expenses": "Salaries",
    #     "desc_departments": "HR, R&D",
    #     "desc_standards": "GAAP",
    #     "desc_compliance": "GST",
    #     "desc_country": "India"
    # })
    # df_coa = parse_coa_string(coa_string)
    # print(df_coa)

    ################
    # res = chain_column_selector.invoke(input={"column_names_str": "Tran Date,Value Date,CHQNO,Transaction Information,Tran Value,D/C,Balance(INR),Branch Name, Debit Amounts, Credit Amounts"})
    # print(res)

    ################
    # df_coa = pd.read_csv(INPUT_COA)
    # df_uncat_trx = pd.read_csv(INPUT_UNCATEGORIZED_TRX)

    # res = category_predictor_app.invoke(
    #     input={
    #         "input_coa_df": df_coa,
    #         "input_uncategorized_transactions_df": df_uncat_trx,
    #         "input_training_df": None
    #     }
    # )

    # ################
    # df_uncat_trx = pd.read_csv(INPUT_T2_UNCAT_TRX)

    # images_list = []
    # with open(INPUT_IMGS) as f:
    #     images_list = json.load(f)

    # with open(INPUT_T2_BILLS) as f:
    #     input_bills = json.load(f)

    # with open(INPUT_T2_INVOICES) as f:
    #     input_invoices = json.load(f)

    # print("DEBUG")

    # res = predictor_app.invoke(
    #     {
    #         "input_company_id": "9341453576607546",
    #         "input_uncategorized_transactions_df": df_uncat_trx,
    #         "input_payment_advise": images_list,
    #         "input_api_bills": input_bills,
    #         "input_api_invoices": input_invoices
    #     }
    # )

    # print("DEBUG END")

    #################
    # res = chain_image_data_extractor.invoke(input={"encoded_image_url": images_list[1]})
    # print(res)

    # #################
    # revenue_accounts, expense_accounts = get_categories(include=["id", "name"])
    # res = chain_category_predictor.invoke(
    #     input={"trx_desc": "UPI 1110202 MORGAN MORGAN", "trx_payee": "Morgan & Morgan Firm", "json_categories": json.dumps(expense_accounts)}
    # )
    # print(res)
    # print("DEBUG")

    #################
    # df_uncat_trx = pd.read_csv(INPUT_T3_UNCAT_TRX, index_col=False)

    # desc_list = list(df_uncat_trx["Description"])
    # types = list(df_uncat_trx["Trx Type"])

    # input_list = [{"description": d, "type": t} for d, t in zip(desc_list, types)]


    # res = chain_description_parser.invoke(
    #     input={
    #         "company_name": "Potu IT Solutions",
    #         "company_nature": "IT Services",
    #         "company_location": "Hyderabad, India",
    #         "trx_desc_list": input_list[10:20],
    #     }
    # )
    # print(res)
    
    ##################
    # search = lambda q: search_store(query=q, collection_name="9341453717615023", k=50, threshold=0.29)
    # res = search("HJ Solutions LLC")
    # print("________ RESULTS ________")
    # print(res)
    
    from rapidfuzz import process, fuzz

    def return_results(list_of_dicts, dict_key, query, threshold):
        scores = []
        for index, item in enumerate(list_of_dicts):
            value = item[dict_key]
            ratio = fuzz.ratio(str(query), str(value))
            scores.append({ "index": index, "score": ratio})

        filtered_scores = [item for item in scores if item['score'] >= threshold]
        sorted_filtered_scores = sorted(filtered_scores, key = lambda k: k['score'], reverse=True)
        filtered_list_of_dicts = [ list_of_dicts[item["index"]] for item in sorted_filtered_scores ]
        return filtered_list_of_dicts
    
    def _query_clean(q: str) -> str:
        clean_q = ''.join(e for e in q if e.isalnum())
        clean_q = clean_q.lower().replace(' ', '')  
        return clean_q  
    
    vs, data = get_vector_store_debug("9341453717615023")
    
    docs = [{"id":uid, "doc":doc, "metadata": metadata}  for uid, doc, metadata in zip(data['ids'], data['documents'], data['metadatas'])]
    
    query = _query_clean("JUDGETECHENFTP")
    
    print(docs)
    print("DEBUG")
    
    return_results(docs, 'doc', query, 10)