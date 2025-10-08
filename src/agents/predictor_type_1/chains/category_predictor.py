import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic

# Prompts
SYSTEM_PROMPT = """
            You are provided with 2 different input JSON objects:

            Input 1. You are provided with a JSON object containing the TRANSACTION DETAILS along with their IDs in the following format:
            {{
                "transactions": [
                    {{
                        "id": exampleID,
                        "type": credit/debit,
                        "amount": amount_number_1,
                        "transaction_description": "example0"
                    }},
                    {{
                        "id": exampleID,
                        "type": credit/debit,
                        "amount": amount_number_1,
                        "transaction_description": "example1"
                    }},
                    ....
                ]
            }}
            
            Input 2. You are also provided a JSON object containing the CATEGORY NAMES along with the CATEGORY CLASSES in the following format:
            {{
                "categories": [
                    {{
                        "category_name": name1,
                        "category_class": one of income/expense/asset/liability/equity
                    }},
                    {{
                        "category_name": name2,
                        "category_class": one of income/expense/asset/liability/equity
                    }},
                    ....
                ]
            }}
                        
            Here is what you are expected to do:
            - Your main task is to analyze each transaction's description from the TRANSACTIONS input object (Input 1), identify who the payee is and classify it into ONE of the "category_name" from the input list of CATEGORIES JSON object (Input 2). The identified payee in the description, the amount and the type the transaction may help you in classifying it into one of the category names
            
            - You also need to report a number on a scale of 1 to 10 about how confident you are that the "category_name" that you classified for a transaction description, perfectly matches the transaction description. You only use default terms like "Other" etc when you're unsure.
            
            - You will also need to go through the transaction's description and identify if the name of the payee (it can be any name in the transaction description like person/company/entity etc.). if you are unable to identify the payee, then set the field to null in the output json.

            - You will finally return the 3 newly identified fields' information as a JSON in the following format (which reuses the id and transaction_description fields from the input format):
            {{
                "transactions: [
                    {{
                        "id": exampleID,
                        "transaction_description": "example0",
                        "category_name": "example_category",
                        "category_pred_conf": confidence_score_number,
                        "payee": "identified_payee_0"
                    }},
                    {{
                        "id": exampleID,
                        "transaction_description": "example1",
                        "category_name": "example_category",
                        "category_pred_conf": confidence_score_number,
                        "payee": "identified_payee_1"
                    }},
                    ....
                ]
            }}
            
            Additional context:
            - in the input categories, each "category_name" has a "category_class".
            - "category_class" can only be one of the following: (Income / Expense / Asset / Liability / Equity)
            - The "category_class" field will be helpful in classifying the "category_name" for a transaction in the following way:
                - A "Credit" type transaction can most likely be classified as a "category_name" which belongs to (Income / Liability / Equity) category classes
                - A "Debit" type transaction can most likely be classified as a "category_name" which belongs to (Asset / Expense) category classes

            IMPORTANT:
            - The picked category for each transaction can only be one of the "category_name" fields in the list of category objects. Ensure its from this list
            - DO NOT MODIFY the content in the fields "id" and "transaction_description", just retain them AS IS and create the fields "category_name", "category_pred_conf" and "payee"
            - you will return the JSON only and no additional text.
            - ensure you stick to the correct output format
            - ensure that all the transactions are processed and none are missed
"""

prompt_category_predictor_json = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
            Here are your inputs:
            
            1. JSON containing transaction information :
            
            {json_trx_desc}
            
            2. JSON containing category names:
            
            {json_categories}
            """,
        ),
    ],
    input_variables=["json_trx_desc", "json_categories"],
)


# Model
# llm = ChatAnthropic(model_name="claude-3-5-sonnet-latest")
# Azure OpenAI (Primary)
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
    temperature=0
)

# Parser
parser = JsonOutputParser()

# Chains
chain_category_predictor_json = prompt_category_predictor_json | llm | parser
