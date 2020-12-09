import os
from flask import Flask, jsonify, redirect, request, Response
from flag_data.FlaggingMongo import FlaggingMongo
from handlers.FlaggingAPI import make_routes

def _create_flagging_mongo():
    return FlaggingMongo("mongodb://localhost:27017/flagging")

app = Flask(__name__)
# app.register_blueprint(flag_api)

#configure secret key
app.secret_key = os.urandom(24).hex()
flagging_mongo = _create_flagging_mongo()
make_routes(app, flagging_mongo)

if __name__ == "__main__":
    app.run(debug=True)



