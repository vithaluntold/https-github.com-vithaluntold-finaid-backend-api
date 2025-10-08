from langgraph.graph import START, END, StateGraph

from src.agents.predictor_type_1.graphs.app_csv.state import GraphState
from src.agents.predictor_type_1.graphs.app_csv.consts import (
    COLUMN_SELECT,
    STANDARDIZE_INPUT,
    CREATE_INPUT_OBJECTS,
    CATEGORY_PREDICT,
    VALUES_SELECT_TRX,
    FINAL_CLEANUP
)
from src.agents.predictor_type_1.graphs.app_csv.nodes import (
    node_column_selection,
    node_standardize_input,
    node_create_input_objects,
    node_category_prediction,
    node_trx_values_selection,
    node_final_cleanup
)


# Condition checkers
def check_csv_type(state: GraphState) -> str:
    p_col_names = state["predicted_column_names"]
    p_type = p_col_names["type"]
    if p_type == 1:
        return CREATE_INPUT_OBJECTS
    elif p_type == 2:
        return STANDARDIZE_INPUT
    else:
        raise RuntimeError(f"Unknown Sheet Type: {p_type}")


# Set Graph Nodes
workflow = StateGraph(GraphState)
workflow.add_node(COLUMN_SELECT, node_column_selection)
workflow.add_node(STANDARDIZE_INPUT, node_standardize_input)
workflow.add_node(CREATE_INPUT_OBJECTS, node_create_input_objects)
workflow.add_node(CATEGORY_PREDICT, node_category_prediction)
workflow.add_node(VALUES_SELECT_TRX, node_trx_values_selection)
workflow.add_node(FINAL_CLEANUP, node_final_cleanup)

# Set Graph Edges
workflow.add_edge(START, COLUMN_SELECT)
workflow.add_conditional_edges(COLUMN_SELECT, check_csv_type)
workflow.add_edge(STANDARDIZE_INPUT, CREATE_INPUT_OBJECTS)
workflow.add_edge(CREATE_INPUT_OBJECTS, CATEGORY_PREDICT)
workflow.add_edge(CATEGORY_PREDICT, VALUES_SELECT_TRX)
workflow.add_edge(VALUES_SELECT_TRX, FINAL_CLEANUP)
workflow.add_edge(FINAL_CLEANUP, END)

category_predictor_app_csv = workflow.compile()
