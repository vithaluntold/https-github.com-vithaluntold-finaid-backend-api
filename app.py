from dotenv import load_dotenv
load_dotenv()

from src.server import config, app

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
