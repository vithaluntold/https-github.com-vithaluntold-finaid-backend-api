import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic

# Prompts
SYSTEM_PROMPT = """
            You are provided with the following information:
            1. our company's name
            2. the nature of our company's business
            3. transaction description
            4. the parsed description which will be more readable (if available)
            5. who sent/received the money

            6. You will also be provided with a JSON list of account names relevant to the transaction and their IDs in the following format:

            [
                {{
                    "id": id1,
                    "name": name1
                }},
                {{
                    "id": id2,
                    "name": name2
                }},
                ....
            ]
            
            Your main task is to identify which of the account names perfectly matches with the above provided information and return the appropriate one in the form of a JSON like so:
            
            {{
                "id": id2,
                "name": name2
            }}
            
            IMPORTANT: use the information available at your disposal like our company's nature could influence which category is picked.
            
            IMPORTANT: return only the JSON and no other additional information.
"""

prompt_category_predictor = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
            Here are your inputs:
            1. Our company's name:
            {company_name}
            
            2. Out company's nature:
            {company_nature}
            
            3. Transaction description:
            {trx_desc}
            
            4. Parsed description:
            {trx_desc_parsed}
            
            5. Payee/Payer:
            {trx_payee}
        
            3. JSON containing account names:
            {json_categories}
            """,
        ),
    ],
    input_variables=["company_name", "company_nature", "trx_desc", "trx_desc_parsed", "trx_payee", "json_categories"],
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
chain_category_predictor = prompt_category_predictor | llm | parser
