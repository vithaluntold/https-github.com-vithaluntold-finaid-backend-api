import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_openai.chat_models import AzureChatOpenAI

# Prompts
SYSTEM_PROMPT = """
            You are provided with the following information:
            1. Our company's name
            2. The nature of our company's business
            3. The location where our company operates
            4. A JSON list of transaction descriptions and type of transaction (like credit/debit, spent/received) from the bank transactions of our company in the following format:

            [
                {{
                    "description": description1,
                    "type": credit/debit
                }},
                {{
                    "description": description2,
                    "type": credit/debit
                }},
                ....
            ]


            Your main task is to:
            - analyze each transaction description and try to parse out the name of the company or person or any other entity who is the other party of the transaction
            - account for information like our company's name, nature and location while understanding the other party in the transaction description as more often than not, the descriptions have multiple names
            - after identifying the payee make the text more human readable
            - in some cases a group of words are mashed together (like A company like Apple Services Inc, would be represented like APPLESERVINC) You need to make this text more human readable to the best of your ability, in this case the expected answer would be 'Apple Serv Inc'
            - you will also identify the type of transaction which can be one of the following: [TRANSFER, INTERNAL_TRANSFER, CREDIT_CARD_PAYMENT, CHECK, UNKNOWN]
            - Note that a credit payments for loans like vehicle loan etc cannot come under CREDIT_CARD_PAYMENT
            - return the readable parsed payee in an ordered list, in the same order as the input like so:
            
            [
                {{
                    "payee": payee1,
                    "type": TRANSFER
                }},
                {{
                    "payee": payee2,
                    "type": CHECK
                }},
                ...
            ]
            
            Here are a few examples of outliers and their expected outputs:            
            
            input: System-recorded fee for QuickBooks Payments. Fee-name: DiscountRateFee, fee-type: Daily
            output: QuickBooks Payments
            
            input: Texas SDU       CHILDSUPP XXXXXXXXXXXX003849772-Texas SDU       CHILDSUPP XXXXXXXXXXXX003849772
            output: Child Support
            
            input: Pay Period: 01/27/2025-02/02/2025
            output: Payroll

            IMPORTANT THINGS TO NOTE: 
            - return only the JSON and no other additional information.
            - ignore known bank names in the description and try to look for proper nouns like people/organizations.
            - if no proper nouns are found, return an empty string for that transaction.
"""

prompt_description_parser = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
            Here is your input:
            
            1. Our company's name: {company_name}
            2. Nature of our company's business: {company_nature}
            3. Location of our company: {company_location}
            4. Transaction descriptions list:
            {trx_desc_list}
            """,
        ),
    ],
    input_variables=["company_name", "company_nature", "company_location", "trx_desc_list"],
)

# Model - Azure OpenAI Configuration
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    model_name=os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")
)
# Alternative: llm = ChatOpenAI(model="gpt-4o")

# Parser
parser = JsonOutputParser()

# Chains
chain_description_parser = prompt_description_parser | llm | parser