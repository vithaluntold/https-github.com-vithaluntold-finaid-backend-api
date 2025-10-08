from langgraph.graph import START, END, StateGraph

from src.agents.predictor_type_2.graphs.app.state import GraphState
from src.agents.predictor_type_2.graphs.app.consts import (
    N1_COLUMN_SELECT,
    N1A_STANDARDIZE_INPUT,
    N2_VALUES_SELECT_TRX,
    N3_CREATE_INPUT_OBJECTS,
    N3A_DESCRIPTION_PARSING,
    N4_VECTOR_STORE_SEARCH,
    N4A_PREDICT_PAYMENT_ADVISE,
    N5_POPULATE_VECTOR_DATA,
    N6_PROCESS_VC_INITIAL,
    N6X_PROCESS_PAYMENT_ADVISE,
    N7A_PROCESS_VENDOR_BILL,
    N7B_PROCESS_CUSTOMER_INVOICE,
    N8_PROCESS_VC_FINAL,
    N9_PROCESS_UNKNOWN_PAYEES
)

from src.agents.predictor_type_2.graphs.app.nodes import (
    node_1_column_selection,
    node_1a_standardize_input,
    node_2_trx_values_selection,
    node_3_create_input_objects,
    node_3a_description_parsing,
    node_4_search_vector_store,
    node_4a_detect_payment_advise,
    node_5_populate_vector_data,
    node_6_process_vc_initial,
    node_6x_process_payment_advise,
    node_7a_process_vendor_bill,
    node_7b_process_customer_invoice,
    node_8_process_vc_final,
    node_9_process_unknown_payees
)


# Condition checkers
def check_csv_type(state: GraphState) -> str:
    p_col_names = state["predicted_column_names"]
    p_type = p_col_names["type"]
    if p_type == 1:
        return N2_VALUES_SELECT_TRX
    elif p_type == 2:
        return N1A_STANDARDIZE_INPUT
    else:
        raise RuntimeError(f"Unknown Sheet Type: {p_type}")


# Set Graph Nodes
workflow = StateGraph(GraphState)
workflow.add_node(N1_COLUMN_SELECT, node_1_column_selection)
workflow.add_node(N1A_STANDARDIZE_INPUT, node_1a_standardize_input)
workflow.add_node(N2_VALUES_SELECT_TRX, node_2_trx_values_selection)
workflow.add_node(N3_CREATE_INPUT_OBJECTS, node_3_create_input_objects)
workflow.add_node(N3A_DESCRIPTION_PARSING, node_3a_description_parsing)
workflow.add_node(N4_VECTOR_STORE_SEARCH, node_4_search_vector_store)
workflow.add_node(N4A_PREDICT_PAYMENT_ADVISE, node_4a_detect_payment_advise)
workflow.add_node(N5_POPULATE_VECTOR_DATA, node_5_populate_vector_data)
workflow.add_node(N6X_PROCESS_PAYMENT_ADVISE, node_6x_process_payment_advise)
workflow.add_node(N6_PROCESS_VC_INITIAL, node_6_process_vc_initial)
workflow.add_node(N7A_PROCESS_VENDOR_BILL, node_7a_process_vendor_bill)
workflow.add_node(N7B_PROCESS_CUSTOMER_INVOICE, node_7b_process_customer_invoice)
workflow.add_node(N8_PROCESS_VC_FINAL, node_8_process_vc_final)
workflow.add_node(N9_PROCESS_UNKNOWN_PAYEES, node_9_process_unknown_payees)


# Set Graph Edges
workflow.add_edge(START, N1_COLUMN_SELECT)
workflow.add_conditional_edges(N1_COLUMN_SELECT, check_csv_type)
workflow.add_edge(N1A_STANDARDIZE_INPUT, N2_VALUES_SELECT_TRX)
workflow.add_edge(N2_VALUES_SELECT_TRX, N3_CREATE_INPUT_OBJECTS)
workflow.add_edge(N3_CREATE_INPUT_OBJECTS, N3A_DESCRIPTION_PARSING)
workflow.add_edge(N3A_DESCRIPTION_PARSING, N4_VECTOR_STORE_SEARCH)
workflow.add_edge(N3A_DESCRIPTION_PARSING, N4A_PREDICT_PAYMENT_ADVISE)
workflow.add_edge(N4_VECTOR_STORE_SEARCH, N5_POPULATE_VECTOR_DATA)
workflow.add_edge(N4A_PREDICT_PAYMENT_ADVISE, N5_POPULATE_VECTOR_DATA)
workflow.add_edge(N5_POPULATE_VECTOR_DATA, N6X_PROCESS_PAYMENT_ADVISE)
workflow.add_edge(N6X_PROCESS_PAYMENT_ADVISE, N6_PROCESS_VC_INITIAL)
workflow.add_edge(N6_PROCESS_VC_INITIAL, N7A_PROCESS_VENDOR_BILL)
workflow.add_edge(N7A_PROCESS_VENDOR_BILL, N7B_PROCESS_CUSTOMER_INVOICE)
workflow.add_edge(N7B_PROCESS_CUSTOMER_INVOICE, N8_PROCESS_VC_FINAL)
workflow.add_edge(N8_PROCESS_VC_FINAL, N9_PROCESS_UNKNOWN_PAYEES)
workflow.add_edge(N9_PROCESS_UNKNOWN_PAYEES, END)

predictor_app = workflow.compile()
