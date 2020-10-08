import flask
import os
from flask import Flask



#intialize app
app = Flask(__name__)

#configure secret key
app.secret_key = os.urandom(24).hex()

#hello world
@app.route('/')
def hello_world():
    return "Hello, World!"




#housekeeeping
if __name__ == "__main__":
    app.run(debug=True)

