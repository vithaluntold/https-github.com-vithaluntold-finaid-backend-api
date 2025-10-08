from flask import Blueprint
from src.server.controllers import (
    test_controller,
    coa_generator_controller,
    category_predictor_controller,
    sheet_functions_controller,
    vector_store_controller,
    crm_predictor_controller
)

# main blueprint to be registered with application
api = Blueprint("api", __name__)

# register controllers with api blueprint
api.register_blueprint(test_controller.tests, url_prefix="/tests")
api.register_blueprint(coa_generator_controller.coa_generator, url_prefix="/coa-generator")
api.register_blueprint(category_predictor_controller.category_predictor, url_prefix="/category-predictor")
api.register_blueprint(sheet_functions_controller.sheet_functions, url_prefix="/sheet-functions")
api.register_blueprint(vector_store_controller.vector_store, url_prefix="/vector-store")
api.register_blueprint(crm_predictor_controller.crm_predictor, url_prefix="/crm-predictor")
