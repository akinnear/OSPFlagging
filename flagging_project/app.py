import os
from flask import Flask, jsonify, redirect, request, Response
from flag_data.FlaggingDOA import FlaggingDOA
from handlers.FlaggingAPI import make_routes

def _create_flagging_doa():
    return FlaggingDOA("mongodb://localhost:27017/flagging")

app = Flask(__name__)
# app.register_blueprint(flag_api)

#configure secret key
app.secret_key = os.urandom(24).hex()
flagging_doa = _create_flagging_doa()
make_routes(app, flagging_doa)

if __name__ == "__main__":
    app.run(debug=True)



