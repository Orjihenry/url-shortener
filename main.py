from flask import Flask, render_template
from config import app_config


app = Flask(__name__)

app.config.from_object(app_config)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
