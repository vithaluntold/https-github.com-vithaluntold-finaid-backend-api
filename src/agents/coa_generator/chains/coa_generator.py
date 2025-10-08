import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic

# Prompts
SYSTEM_PROMPT = """
            You are a Finance, Accounting, Tax, and Audit expert with expertise in the USA, UK, Canada, and India. You only provide detailed insights on these subjects using official sources such as the IRS, SEC, HMRC, and MCA. You will avoid and ignore all topics outside compliance, taxation, finance, and accounting, maintaining a sharp focus on your domain expertise.
            
            You are tasked with generating the Chart of accounts based on the user's request.
            
            Follow the following format when generating the Chart of Accounts, ensure that the column names match perfectly:
              - **Account Code**: Numerical or alphanumeric code for the account (if specified by the user, use their sequence, else generate your own).
              - **Account Name**: Name of the account (e.g., Cash, Accounts Receivable).
              - **Account Category**: Category of the account (e.g., Current Assets, Fixed Assets, Current Liabilities, Operating Expenses, Non-Operating Expenses).
              - **Account Class**: Classification of the account (e.g., Asset, Liability, Equity, Expense, Income).
              - **Statement**: Indicates whether it belongs to the Balance Sheet or the Profit or Loss Statement (Profit or Loss, Balance Sheet).
     
            Additional Guidelines for COA Structure:

              - Entity-Specific Accounts: Include entity-based accounts such as Share Capital, Retained Earnings, Member Contributions, etc.
              - Tax Accounts: Add mandatory tax accounts based on jurisdiction (e.g., USA, India, UAE).
              - Expense Categories: Include key expenses like COGS, Salaries, Rent, Utilities, Marketing, etc.
              - For the generated column **Account Class**:
                - ensure that the values are only one of [Asset, Liability, Equity, Expense, Income]
                - make sure the spelling is exact
              - For the generated column **Statement**:
                - ensure that the values are only one of [Profit or Loss, Balance Sheet]
                - make sure the spelling is exact
                            
            The user might provide the input in either of two forms:
              1. The user might provide these 8 input variables with which you can generate a comprehensive CoA
                - Entity Type: Is the business a Corporation, LLC, Partnership, Sole Proprietorship, or Nonprofit?
                - Industry: What industry does the business operate in (e.g., manufacturing, retail, consulting, nonprofit)?
                - Revenue Sources: What are the main sources of income (e.g., product sales, consulting services, grants)?
                - Expense Categories: List the major expense categories (e.g., salaries, COGS, R&D).
                - Departments: If they need to track income/expenses by department (e.g., sales, R&D, operations)?
                - Reporting Standards: If they follow any specific frameworks such as GAAP, IFRS, or tax-specific guidelines?
                - Compliance Needs: Are there any specific tax or regulatory accounts required (e.g., VAT accounts, GST, Sales Tax Payable)?
                - Scalability: If the Chart of Accounts to be scalable for future growth (e.g., new locations, products)?
              2. Else they might provide a partial CSV with the Account Names. You will have to just generate the other missing fields columns in this case.
                - In this case, make sure none of the input data is left out in the generated output

            IMPORTANT: Return the CSV only and do not return any additional text. Use "," as the separator for the CSV.
            """

prompt_coa_generator_csv = ChatPromptTemplate(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
            With the following CSV data, generate a Chart of Accounts for a company:
    
            {csv_data}

            IMPORTANT: Return the CSV only and do not return any additional text. Use "," as the separator for the CSV.
            """,
        ),
    ]
)

"""
desc_business
desc_industry
desc_revenue_sources
desc_primary_expenses
desc_departments
desc_standards
desc_compliance
desc_country
"""
prompt_coa_generator_desc = ChatPromptTemplate(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
            Design a comprehensive Chart of Accounts for a business structured like the following:
            
            - Entity Type: {desc_business}
            - Industry: {desc_industry}
            - Revenue Sources: {desc_revenue_sources}
            - Expense Categories: {desc_primary_expenses}
            - Departments: {desc_departments}
            - Reporting Standards: {desc_standards}
            - Compliance Needs: {desc_compliance}
            - Scalability: {desc_country}
            
            IMPORTANT: Return the CSV only and do not return any additional text. Use "," as the separator for the CSV.
            """,
        ),
    ]
)

# Output Parser
output_parser = StrOutputParser()


# Model - Azure OpenAI Configuration
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    model_name=os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")
)

# Alternative models (uncomment to use)
# llm = ChatOpenAI(model="gpt-4o")  # Standard OpenAI
# llm = ChatAnthropic(model_name="claude-3-5-sonnet-latest")  # Anthropic

# Chains
chain_coa_generator_csv = prompt_coa_generator_csv | llm | output_parser

chain_coa_generator_desc = prompt_coa_generator_desc | llm | output_parser
