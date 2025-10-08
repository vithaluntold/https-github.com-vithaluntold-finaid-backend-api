import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic

prompt_column_selector = ChatPromptTemplate(
    [
        (
            "system",
            """
            You are provided with just the names of the columns from a bank statement spreadsheet. Each column name is separated by a comma.
            
            You have to identify the following things:
            1. Pick the column name which best describes the term "Transaction Date"
            2. Pick the column name which best describes the term "Transaction Details"
            3. Pick the column name which best describes the term "Transaction Amount"
                - if no such column exists, return null
            4. Pick the column name which best describes the term "Transaction Type" (whether it was a debit or a credit transaction).
                - Ensure this is a common column name which may list both Debit and Credit as values under the column, this CANNOT BE JUST DEBIT OR CREDIT, it must represent both
                - if no such column exists, return null
            5. Pick the column name which best describes the term "Debit Amount"
                - if no such column exists, return null
            6. Pick the column name which best describes the term "Credit Amount"
                - if no such column exists, return null
            7. Finally identify the type of the spreadsheet:
                - if the columns describing the terms "Transaction Details" and "Transaction Amount" exist, then return 1
                - else if the columns describing the terms "Debit Amount" and "Credit Amount" exist, then return 2

            Using the above identified information, construct a json object in the following format:
            {{
                "col_trx_date": identified_column_name0
                "col_trx_description":  identified_column_name1,
                "col_trx_amount":  identified_column_name2 | null,
                "col_trx_type":  identified_column_name3 | null,
                "col_debit": identified_column_name | null
                "col_credit": identified_column_name | null
                "type": 1 | 2 based on type of the spreadsheet
            }}
            
            Example 1:
            Input given to you: 
            [Trx date, Time, Amount(INR), Balance(INR), Chq Details, Acc no.,  Transaction Particulars, Id, Cr / Dr]
            
            Expected output:
            {{
                "col_trx_date": "Trx Date",
                "col_trx_description":  "Transaction Particulars",
                "col_trx_amount":  "Amount(INR)",
                "col_trx_type":  "Cr / Dr",
                "col_debit": null,
                "col_credit": null,
                "type": 1
            }}

            Example 2:
            Input given to you: 
            [Tran Date, Chq No, Particulars, Debit, Credit, Balance, Init. Br]
            
            Expected output:
            {{
                "col_trx_date": "Tran Date",
                "col_trx_description":  "Particulars",
                "col_trx_amount":  null,
                "col_trx_type":  null,
                "col_debit": "Debit",
                "col_credit": "Credit",
                "type": 2
            }}
         

            IMPORTANT: 
            - ensure that the output JSON format is strictly followed.
            - return ONLY the JSON, do not return any other text.
            """,
        ),
        (
            "human",
            """
            Here are your inputs:
            [{column_names_str}]
            """,
        ),
    ]
)


# Output Parser
output_parser = JsonOutputParser()

# Model
# Azure OpenAI (Primary)
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    model=os.getenv("AZURE_OPENAI_MODEL_NAME"),
    temperature=0
)

# Chains
chain_column_selector = prompt_column_selector | llm | output_parser