#!/usr/bin/env python3

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
from decimal import Decimal, ROUND_HALF_UP
import os
import traceback

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config["SQLALCHEMY_DATABASE_URI"] = (
     environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/cards"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Define Card model
class Card(db.Model):
    __tablename__ = 'cards'
    CardId = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, nullable=False)
    Balance = db.Column(db.Numeric(10,2), nullable=False)
    CardSerialNumber = db.Column(db.String(20), unique=True, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            "CardId": self.CardId,
            "UserId": self.UserId,
            "Balance": float(self.Balance),
            "CardSerialNumber": self.CardSerialNumber,
            "CreatedAt": self.CreatedAt.isoformat(),
            "UpdatedAt": self.UpdatedAt.isoformat()
        }

# Function to initialize the database and seed data
def initialize_database():
    # Create tables if they don't exist
    db.create_all()

    # Seed the database with initial data if empty
    if not Card.query.first():
        initial_cards = [
            Card(UserId=1, Balance=0.00, CardSerialNumber="SN1234567890", CreatedAt="2025-03-15 09:00:00", UpdatedAt="2025-03-15 09:00:00"),
            Card(UserId=2, Balance=0.00, CardSerialNumber="SN9876543210", CreatedAt="2025-03-15 09:00:00", UpdatedAt="2025-03-15 09:00:00"),
        ]
        db.session.add_all(initial_cards)
        db.session.commit()
        print("Database initialized with sample data.")

# CREATE
@app.route("/cards", methods=['POST'])
def createCard():
    if request.is_json:
        try:
            data = request.get_json()
            print("Received card creation request with data:", data)  # Debug log
            
            # Validate required fields
            if 'UserId' not in data:
                return jsonify({
                    "code": 400,
                    "message": "UserId is required"
                }), 400
                
            # Ensure UserId is an integer
            try:
                user_id = int(data['UserId'])
                data['UserId'] = user_id
            except (ValueError, TypeError):
                return jsonify({
                    "code": 400,
                    "message": "UserId must be an integer"
                }), 400
                
            result = processCreateCard(data)
            return jsonify(result), result["code"]
        except Exception as e:
            # Get the full stack trace
            stack_trace = traceback.format_exc()
            print("Error in card creation:", str(e))
            print("Stack trace:", stack_trace)
            
            return jsonify({
                "code": 500,
                "message": f"Error creating card: {str(e)}",
                "details": stack_trace
            }), 500
    else:
        return jsonify({
            "code": 400,
            "message": "Request must be JSON"
        }), 400

# READ
@app.route("/cards", methods=['GET'])
def getCards():
    try:
        # Get user_id from query parameter
        user_id = request.args.get('user_id', type=int)
        
        if user_id:
            # Filter cards by user_id
            cards = Card.query.filter_by(UserId=user_id).all()
        else:
            # Get all cards if no user_id specified
            cards = Card.query.all()
        return jsonify({
            "code": 200,
            "data": [card.serialize() for card in cards],
            "message": "Cards retrieved successfully"
        }), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

# READ SINGLE
@app.route("/cards/<int:card_id>", methods=['GET'])
def getCard(card_id):
    try:
        card = Card.query.get(card_id)
        if card:
            return jsonify(card.serialize()), 200
        return jsonify({"code": 404, "message": "Card not found"}), 404
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

# UPDATE
@app.route("/cards/<int:card_id>", methods=['PUT'])
def updateCard(card_id):
    if request.is_json:
        try:
            data = request.get_json()
            result = processUpdateCard(card_id, data)
            return jsonify(result), result["code"]
        except Exception as e:
            return jsonify({"code": 500, "message": str(e)}), 500
    else:
        return jsonify({
            "code": 400,
            "message": "Card update should be in JSON."
        }), 400

# DELETE
@app.route("/cards/<int:card_id>", methods=['DELETE'])
def deleteCard(card_id):
    try:
        result = processDeleteCard(card_id)
        return jsonify(result), result["code"]
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

def processCreateCard(data):
    try:
        print("Processing card creation with data:", data)
        
        # Generate serial number if not provided
        serial_number = data.get('CardSerialNumber') or generate_serial_number()
        
        # Convert Balance to Decimal if provided, default to 0
        try:
            balance = Decimal(str(data.get('Balance', 0))).quantize(Decimal('0.00'))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            raise ValueError(f"Invalid balance value: {str(e)}")
        
        print(f"Creating new card with serial number: {serial_number}")
        
        new_card = Card(
            UserId=data['UserId'],
            Balance=balance,
            CardSerialNumber=serial_number
        )
        
        print("Attempting database session operations...")
        db.session.add(new_card)
        db.session.commit()
        print("Database commit successful")
        
        created_card = new_card.serialize()
        print("Card created successfully:", created_card)
        
        return {
            "code": 201,
            "data": created_card,
            "message": "Card created successfully"
        }
    except Exception as e:
        print("Error in processCreateCard:", str(e))
        print("Stack trace:", traceback.format_exc())
        db.session.rollback()
        raise e

def processUpdateCard(card_id, data):
    try:
        card = Card.query.get(card_id)
        if not card:
            return {"code": 404, "message": "Card not found"}
        
        if 'UserId' in data:
            card.UserId = data['UserId']
        if 'Balance' in data:
            card.Balance = Decimal(data['Balance'])
        if 'CardSerialNumber' in data:
            card.CardSerialNumber = data['CardSerialNumber']
        
        db.session.commit()
        return {
            "code": 200,
            "data": card.serialize(),
            "message": "Card updated successfully"
        }
    except Exception as e:
        db.session.rollback()
        raise e

def processDeleteCard(card_id):
    try:
        card = Card.query.get(card_id)
        if not card:
            return {"code": 404, "message": "Card not found"}
        
        db.session.delete(card)
        db.session.commit()
        return {
            "code": 200,
            "message": "Card deleted successfully"
        }
    except Exception as e:
        db.session.rollback()
        raise e
    
@app.route("/cards/<int:card_id>/balance", methods=['PATCH'])
def update_card_balance(card_id):
    """Update card balance with atomic increment/decrement support"""
    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "Balance update must be in JSON format"
        }), 400

    data = request.get_json()
    
    # Validate request parameters
    if 'amount' not in data or 'operation' not in data:
        return jsonify({
            "code": 400,
            "message": "Both 'amount' and 'operation' (add/subtract) are required"
        }), 400

    if data['operation'] not in ['add', 'subtract']:
        return jsonify({
            "code": 400,
            "message": "Invalid operation. Use 'add' or 'subtract'"
        }), 400

    try:
        amount = Decimal(str(data['amount'])).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError) as e:
        return jsonify({
            "code": 400,
            "message": f"Invalid amount: {str(e)}"
        }), 400

    try:
        card = Card.query.get(card_id)
        if not card:
            return jsonify({
                "code": 404,
                "message": "Card not found"
            }), 404
        
        # Perform atomic balance update
        if data['operation'] == 'add':
            card.Balance += amount
        else:
            if card.Balance < amount:
                return jsonify({
                    "code": 400,
                    "message": "Insufficient balance for subtraction"
                }), 400
            card.Balance -= amount

        db.session.commit()
        return jsonify({
            "code": 200,
            "data": card.serialize(),
            "message": "Balance updated successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": f"Balance update failed: {str(e)}"
        }), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("This is flask " + os.path.basename(__file__) + ": card management ...")
    app.run(host='0.0.0.0', port=5203, debug=True)
