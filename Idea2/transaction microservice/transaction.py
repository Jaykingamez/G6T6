#!/usr/bin/env python3

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/transactions"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    TransactionId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserId = db.Column(db.Integer, nullable=False)
    CardId = db.Column(db.Integer, nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    PaymentMethod = db.Column(db.Enum('STRIPE', 'PAYPAL'), nullable=True)
    Status = db.Column(db.Enum('SUCCESS', 'FAILED', 'PENDING'), nullable=False, default='PENDING')
    PreviousBalance = db.Column(db.Numeric(10, 2), nullable=False)
    NewBalance = db.Column(db.Numeric(10, 2), nullable=False)
    PaymentId = db.Column(db.Integer, nullable=False)
    CreatedAt = db.Column(db.TIMESTAMP, server_default=db.func.now())
    UpdatedAt = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.now())

    def serialize(self):
        return {
            'TransactionId': self.TransactionId,
            'UserId': self.UserId,
            'CardId': self.CardId,
            'Amount': float(self.Amount),
            'PaymentMethod': self.PaymentMethod,
            'Status': self.Status,
            'PreviousBalance': float(self.PreviousBalance),
            'NewBalance': float(self.NewBalance),
            'PaymentId': self.PaymentId,
            'CreatedAt': self.CreatedAt.isoformat(),
            'UpdatedAt': self.UpdatedAt.isoformat()
        }

# CREATE
@app.route("/transactions", methods=['POST'])
def createTransaction():
    if request.is_json:
        transaction_data = request.get_json()
        result = processCreateTransaction(transaction_data)
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
    transactions = Transaction.query.all()
    return jsonify([t.serialize() for t in transactions]), 200

def processCreateTransaction(transaction_data):
    print("Creating a new transaction:")
    print(transaction_data)
    try:
        new_transaction = Transaction(
            UserId=transaction_data['UserId'],
            CardId=transaction_data['CardId'],
            Amount=transaction_data['Amount'],
            PaymentMethod=transaction_data['PaymentMethod'],
            Status=transaction_data['Status'],
            PreviousBalance=transaction_data['PreviousBalance'],
            NewBalance=transaction_data['NewBalance'],
            PaymentId=transaction_data['PaymentId']
        )
        db.session.add(new_transaction)
        db.session.commit()
        return {
            'code': 201,
            'data': new_transaction.serialize(),
            'message': 'Transaction created successfully.'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'code': 500,
            'data': str(e),
            'message': 'An error occurred while creating the transaction.'
        }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          ": transaction management ...")
    app.run(host='0.0.0.0', port=5206, debug=True)
