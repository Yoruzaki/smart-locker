from flask import Flask, render_template
from flask_cors import CORS

from api import api_bp
from config import config
from database import init_db
from hardware import HardwareController


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["JSON_SORT_KEYS"] = False
    CORS(app)

    init_db()
    app.config["HARDWARE"] = HardwareController(config)
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=config.DEBUG)


