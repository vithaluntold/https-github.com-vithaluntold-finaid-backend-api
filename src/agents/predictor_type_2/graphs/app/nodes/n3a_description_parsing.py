from typing import Any, Dict
from tqdm import tqdm

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.chains import chain_description_parser


def node_3a_description_parsing(state: GraphState) -> Dict[str, Any]:
    print("--- 3A. DESCRIPTION PARSE ---")

    company_name = state["input_company_name"]
    company_nature = state["input_company_nature"]
    company_location = state["input_company_location"]
    input_transactions = state["processed_input_transactions"]
    output_transactions = state["final_output_transactions"]

    chain_input = [
        {"description": trx["transaction_description"], "type": trx["type"]}
        for trx in input_transactions
    ]
    chain_output = []

    batch_size = 20
    list_len = len(chain_input)

    for i in tqdm(range(0, list_len, batch_size)):
        chain_input_sublist = chain_input[i : min(list_len, i + batch_size)]

        res = chain_description_parser.invoke(
            input={
                "company_name": company_name,
                "company_nature": company_nature,
                "company_location": company_location,
                "trx_desc_list": chain_input_sublist,
            }
        )

        chain_output.extend(res)

    for i in range(len(input_transactions)):
        input_transactions[i]["parsed_description"] = chain_output[i]["payee"]
        output_transactions[i]["parsed_description"] = chain_output[i]["payee"]
        input_transactions[i]["parsed_type"] = chain_output[i]["type"]
        output_transactions[i]["parsed_type"] = chain_output[i]["type"]
        if chain_output[i]["payee"] == "":
            output_transactions[i]["message"] = "Description couldn't be parsed"

    return {
        "processed_input_transactions": input_transactions,
        "final_output_transactions": output_transactions,
    }
