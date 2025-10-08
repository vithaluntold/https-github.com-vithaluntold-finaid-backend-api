import os
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_openai.chat_models import AzureChatOpenAI

# Prompt
prompt_template = HumanMessagePromptTemplate.from_template(
    template=[
        {
            "type": "text",
            "text": """
            Here is the name of our company: {company_name}
            Now extract the requested information from the image in the specified format.
            """,
        },
        {"type": "image_url", "image_url": "{encoded_image_url}"},
    ]
)


prompt_image_payment_advise_extractor = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="""
                You'll be provided with the scanned image of a payment advice. From the image, you will need to extract the following details and provide them in a JSON format described below.
                
                The payment advise may be either 1. very clear or 2. cryptic
                
                Incase of cryptic payment advises, here are a few ground rules for the minimal information it will contain:
                - they definitely will have bill/invoice numbers even if they dont have the dates or amounts.
                - they definitely will include the dates and amounts for the transactions, therefore any dates inside which isn't the date of the payment advise will most likely refer to the transaction dates.
                
                The details to be extracted:
                    1. the name of the payer.
                    2. the name of the payee.
                    3. whether the payment advice is for bills or invoices
                    4. bill/invoice aka receipt details in a list with each list item containing:
                        a. receipt id
                        b. receipt date (may or maynot be present)
                        c. receipt amount without any symbols, just the number
                    5. transaction details in a list with each transaction item containing:
                        a. transaction id (may or maynot be present)
                        b. transaction date
                        c. transaction amount without any symbols, just the number

                You will also be provided Our company's name. Incase you encounter those names in the payment advise, you can set those respective fields (payee/payer name) in the response to empty strings ("") as we are only interested in the other party in the transaction not our own company.            
                        
                As far as dates are concerned:
                - Try to deduce if they are in month first or date first formats (MM/DD or DD/MM). If its not possible to deduce, assume that it is MM/DD.
                - If its date first, then convert it to month first and save it as MM/DD/YYYY (save it in this exact format)
                - If its already in month first, just save it as MM/DD/YYYY (save it in this exact format)
                
                The output example:
                    {{
                        "payee": "identified payee",
                        "payer": "identified payer,
                        "type": "bill" or "invoice",
                        "receipt_details": [
                            {{
                                "id": "identified receipt id 1"
                                "date": "identified date" | null
                                "amount": "identified amount"
                            }},
                            {{
                                "id": "identified receipt id 2" | null
                                "date": "identified date" | null
                                "amount": "identified amount"
                            }}
                            ...
                        ],
                        "transaction_details": [
                            {{
                                "id": "identified transaction id 1"
                                "date": "identified date"
                                "amount": "identified amount"
                            }},
                                                        {{
                                "id": "identified transaction id 2"
                                "date": "identified date"
                                "amount": "identified amount"
                            }}
                            ...
                        ]
                    }}
                
                IMPORTANT: RETURN ONLY THE JSON AND NO ADDITIONAL TEXT
            """
        ),
        prompt_template,
    ]
)

# Output Parser
output_parser = JsonOutputParser()

# Model - Azure OpenAI Configuration
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    model_name=os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")
)
# Alternative: llm = ChatAnthropic(model_name="claude-3-5-sonnet-latest")

chain_image_payment_advise_extractor = prompt_image_payment_advise_extractor | llm | output_parser
