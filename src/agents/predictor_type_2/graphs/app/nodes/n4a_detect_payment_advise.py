from typing import Any, Dict

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.chains import chain_image_payment_advise_extractor


def node_4a_detect_payment_advise(state: GraphState) -> Dict[str, Any]:
    print("--- 4a. DETECT PAYMENT ADVISE ---")

    input_company_name = state["input_company_name"]
    input_payment_advise = state["input_payment_advise"]

    predicted_payment_advise = []
    for pa in input_payment_advise:
        predicted_pa = chain_image_payment_advise_extractor.invoke(
            input={"company_name": input_company_name, "encoded_image_url": pa}
        )
        predicted_payment_advise.append(predicted_pa)

    return {"predicted_payment_advise": predicted_payment_advise}
