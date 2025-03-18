#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulated transaction data
transactions = [
    {"id": 1, "amount": 100.0, "description": "Test transaction"},
    {"id": 2, "amount": 200.0, "description": "Another test transaction"}
]

# CREATE
@app.route("/transactions", methods=['POST'])
def createTransaction():
    if request.is_json:
        transaction = request.get_json()
        result = processCreateTransaction(transaction)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid transaction:")
        print(data)
        return jsonify({"code": 400,
                        "data": str(data),
                        "message": "Transaction should be in JSON."}), 400

# READ
@app.route("/transactions", methods=['GET'])
def getTransactions():
    return jsonify(transactions), 200

def processCreateTransaction(transaction):
    print("Creating a new transaction:")
    print(transaction)
    # Simulate success
    code = 201
    message = 'Simulated success in transaction creation.'
    transactions.append(transaction)
    return {
        'code': code,
        'data': transaction,
        'message': message
    }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          ": transaction management ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
