from flask import Flask
from config import app_config


app = Flask(__name__)

app.config.from_object(app_config)


@app.route("/", methods=["GET", "POST"])
def index():
    return "Url Shortener App"


if __name__ == "__main__":
    app.run(debug=True)
