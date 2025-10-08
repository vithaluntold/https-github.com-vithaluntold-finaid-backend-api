import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic

prompt_trx_values_selector = ChatPromptTemplate(
    [
        (
            "system",
            """
            You are provided with the unique values from the "Transaction Type" column of a spreadsheet.
            
            You have to identify the following things:
            1. Pick the value which best describes the term "Debit"
            2. Pick the value which best describes the term "Credit"

            Using the above identified information, construct a json object in the following format:
            {{
                "type_debit": identified_value
                "type_credit": identified_value
            }}
            
            Example 1:
            Input given to you: 
            [DR, CR]
            
            Expected output:
            {{
                "type_debit": "DR"
                "type_credit": "CR"
            }}
            
            Example 2:
            Input given to you: 
            [Withdrawal, Deposit]
            
            Expected output:
            {{
                "type_debit": "Withdrawal"
                "type_credit": "Deposit"
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
            [{type_column_values_str}]
            """,
        ),
    ]
)


# Output Parser
output_parser = JsonOutputParser()

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

# Chains
chain_trx_values_selector = prompt_trx_values_selector | llm | output_parser
