from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

check_balance_url = "http://localhost:5005/checkbalance/<int:user_id>"

@app.route('/makepayment', methods=['POST'])
def MakePayment():
    return ""

if __name__ == "__main__":
    print("Composite service: Make Payment ...")
    app.run(host='0.0.0.0', port=5008, debug=True)