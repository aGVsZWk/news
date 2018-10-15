from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "helloworld"
    return "helloworld100"


if __name__ == '__main__':
    app.run(debug=True)
