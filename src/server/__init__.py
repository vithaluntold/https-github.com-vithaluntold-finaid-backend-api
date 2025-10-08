from flask import Flask
from flask_cors import CORS
from src.server.routes import api
from src.server.config.config import Config


# load dev/prod config
config = Config().dev_config

app = Flask(__name__)
app.env = config.ENV
CORS(app)

# register routes
app.register_blueprint(api, url_prefix="/api")
