import os
from flask import Flask, jsonify, redirect, request, Response
from flag_data.FlaggingDAO import FlaggingDAO
from handlers.FlaggingAPI import make_routes

def _create_flagging_dao():
    return FlaggingDAO("mongodb://localhost:27017/flagging")

app = Flask(__name__)
# app.register_blueprint(flag_api)

#configure secret key
app.secret_key = os.urandom(24).hex()
flagging_dao = _create_flagging_dao()
make_routes(app, flagging_dao)

if __name__ == "__main__":
    app.run(debug=True)



