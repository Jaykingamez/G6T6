#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulated card data
cards = [
    {"id": 1, "card_number": "1234-5678-9012-3456", "expiration_date": "12/2025"},
    {"id": 2, "card_number": "9876-5432-1098-7654", "expiration_date": "06/2026"}
]

# CREATE
@app.route("/cards", methods=['POST'])
def createCard():
    if request.is_json:
        card = request.get_json()
        result = processCreateCard(card)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid card:")
        print(data)
        return jsonify({"code": 400,
                        "data": str(data),
                        "message": "Card should be in JSON."}), 400

# READ
@app.route("/cards", methods=['GET'])
def getCards():
    return jsonify(cards), 200

# UPDATE
@app.route("/cards/<int:card_id>", methods=['PUT'])
def updateCard(card_id):
    if request.is_json:
        card = request.get_json()
        result = processUpdateCard(card_id, card)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid card update:")
        print(data)
        return jsonify({"code": 400,
                        "data": str(data),
                        "message": "Card update should be in JSON."}), 400

# DELETE
@app.route("/cards/<int:card_id>", methods=['DELETE'])
def deleteCard(card_id):
    result = processDeleteCard(card_id)
    return jsonify(result), result["code"]

def processCreateCard(card):
    print("Creating a new card:")
    print(card)
    # Simulate success
    code = 201
    message = 'Simulated success in card creation.'
    cards.append(card)
    return {
        'code': code,
        'data': card,
        'message': message
    }

def processUpdateCard(card_id, card):
    print("Updating a card:")
    print(card)
    # Find the card to update
    for c in cards:
        if c['id'] == card_id:
            c['card_number'] = card['card_number']
            c['expiration_date'] = card['expiration_date']
            code = 200
            message = 'Simulated success in card update.'
            return {
                'code': code,
                'data': c,
                'message': message
            }
    code = 404
    message = 'Card not found.'
    return {
        'code': code,
        'data': None,
        'message': message
    }

def processDeleteCard(card_id):
    print("Deleting a card:")
    print(card_id)
    # Find the card to delete
    for c in cards:
        if c['id'] == card_id:
            cards.remove(c)
            code = 200
            message = 'Simulated success in card deletion.'
            return {
                'code': code,
                'data': None,
                'message': message
            }
    code = 404
    message = 'Card not found.'
    return {
        'code': code,
        'data': None,
        'message': message
    }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          ": card management ...")
    app.run(host='0.0.0.0', port=5003, debug=True)
