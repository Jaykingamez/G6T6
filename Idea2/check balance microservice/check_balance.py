from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

user_URL = "http://user:5201/users"
card_URL = "http://card:5203/cards"


def fetch_user(user_id):
    """Retrieve user details from user service"""
    try:
        response = requests.get(f"{user_URL}/{user_id}")
        print()
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"User service error: {e}")
        return None

def fetch_cards(user_id):
    """Retrieve user's cards from card service"""
    try:
        response = requests.get(card_URL)
        if response.status_code == 200:
            # Extract cards from the 'data' key in the response
            cards_data = response.json().get('data', [])
            # Filter cards by UserId safely using .get()
            return [
                card for card in cards_data 
                if card.get('UserId') == user_id
            ]
        return []
    except requests.exceptions.RequestException as e:
        print(f"Card service error: {e}")
        return None

@app.route('/checkbalance/<int:user_id>', methods=['GET'])
def get_user_cards(user_id):
    # Get user information
    user_response = fetch_user(user_id)
    
    # Check if user exists
    if not user_response or user_response.get('code') != 200:
        return jsonify({
            "code": 404,
            "message": "User not found"
        }), 404

    # Extract user data
    user_data = user_response.get('data', {})
    
    # Get user's cards
    cards = fetch_cards(user_id)
    if cards is None:
        return jsonify({
            "code": 503,
            "message": "Failed to retrieve card information"
        }), 503

    return jsonify({
        "code": 200,
        "data": {
            "user": {
                "UserId": user_data.get('UserId'),
                "FullName": user_data.get('FullName'),
                "Email": user_data.get('Email'),
                "Phone": user_data.get("Phone")
            },
            "cards": [{
                "CardId": card.get('CardId'),
                "CardSerialNumber": card.get('CardSerialNumber'),
                "Balance": card.get('Balance')
            } for card in cards]
        }
    }), 200

if __name__ == "__main__":
    print("Composite service: User Card Balance ...")
    app.run(host='0.0.0.0', port=5205, debug=True)