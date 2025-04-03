from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

check_balance_url = "http://checkbalance:5205/checkbalance/{user_id}"
make_payment_url = "http://make_payment:5208/makepayment"

def check_balance(user_id):
    """Fetch the balance for a given user ID."""
    url = check_balance_url.format(user_id=user_id)
    try:
        # Make the GET request to the check_balance service
        response = requests.get(url, timeout=5)  # Set a timeout for reliability
        if response.status_code == 200:
            # Return the balance data if successful
            return response.json()
        else:
            # Handle error responses
            return {
                "error": f"Failed to fetch balance. Status code: {response.status_code}",
                "details": response.text
            }
    except requests.exceptions.RequestException as e:
        # Handle connection errors or timeouts
        return {"error": f"Error connecting to check_balance service: {str(e)}"}

@app.route('/top_up/<int:user_id>/<int:card_id>', methods=['POST'])
def top_up(user_id, card_id):
    """Top up card balance."""
    if not request.is_json:
        return jsonify({"code": 400, "message": "Request must be JSON"}), 400

    data = request.get_json()
    amount = data.get("amount")
    
    # Get balance info
    balance_info = check_balance(user_id)
    
    if 'error' in balance_info:
        return jsonify({
            "code": 500,
            "message": balance_info['error']
        }), 500

    # Extract user data safely
    user_data = balance_info.get('data', {}).get('user', {})
    card_data = balance_info.get('data', {}).get('cards', [])
    if not user_data:
        return jsonify({"code": 404, "message": "User data not found"}), 404
    phone_number = user_data.get("Phone")
    if not phone_number:
        return jsonify({"code": 400, "message": "Phone number not found"}), 400
        
    # Get and validate balance
    try:
        currBalance = float(card_data[0].get("Balance"))  # Convert to float early
        if currBalance is None:
            raise ValueError("Balance field missing")
    except (TypeError, IndexError, ValueError) as e:
        return jsonify({"code": 400, "message": f"Invalid balance data: {str(e)}"}), 400

    # Process payment
    try:
        payment_response = requests.post(
            "http://make_payment:5208/makepayment",
            json={
                "amount": int(float(amount) * 100),
                "card_id": card_id,
                "user_id": user_id,
                "phone_number": phone_number,
                "Balance": float(currBalance)
            },
            timeout=10
        )
        
        if payment_response.status_code != 200:
            return jsonify({
                "code": payment_response.status_code,
                "message": "Payment failed",
                "details": payment_response.text
            }), payment_response.status_code
            
        return payment_response.json()
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


if __name__ == "__main__":
    print("Starting Top-Up Service...")
    app.run(host="0.0.0.0", port=5212, debug=True)