from flask import Flask
import limiter

app = Flask(__name__)


@app.route("/")
@limiter.limit_in_a_minute(5)
def hello():
    return "Hello, World!"


app.run(host="0.0.0.0", port=8080, debug=True)
