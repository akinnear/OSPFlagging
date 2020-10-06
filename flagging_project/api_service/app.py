import flask
from flask import Flask

#intialize app
app = Flask(__name__)

#hello world
@app.route('/')
def hello_world():
    return "Hello, World!"

#housekeeeping
if __name__ == "__main__":
    app.run(debug=True)

