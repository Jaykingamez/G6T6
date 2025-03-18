from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

check_balance_url = "http://localhost:5005/checkbalance/<int:user_id>"
make_payment_url = "http://localhost:5008/makepayment"

@app.route('/top_up', methods=['POST'])
def top_up():
    """Top up card balance."""
    if not request.is_json:
        return jsonify({"code": 400, "message": "Request must be JSON"}), 400

    data = request.get_json()
    user_id = data.get("userId")
    card_id = data.get("cardId")
    amount = data.get("amount")

    if not user_id or not card_id or not amount:
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    # Step 1: Fetch current balance using Check Balance service
    try:
        response = requests.get(check_balance_url.format(user_id=user_id))
        if response.status_code == 200:
            balance_data = response.json()
        else:
            return jsonify({"code": 500, "message": "Failed to fetch current balance"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error fetching balance: {str(e)}"}), 500

    # Step 2: Process payment (mocked for simplicity)
    payment_status = "succeeded"  # Mock payment status
    payment_id = "mock_payment_id"  # Mock payment ID

    if payment_status != "succeeded":
        return jsonify({"code": 500, "message": "Payment failed"}), 500

    # Step 3: Update card balance via HTTP PATCH
    new_balance = float(balance_data["data"]["cards"][0]["Balance"]) + float(amount)
    try:
        patch_response = requests.patch(
            f"http://localhost:5003/cards/{card_id}",
            json={"Balance": new_balance}
        )
        if patch_response.status_code != 200:
            return jsonify({"code": 500, "message": "Failed to update card balance"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error updating card balance: {str(e)}"}), 500

    # Step 4: Notify user via Twilio (mocked for simplicity)
    notification_message = f"Your card has been topped up with ${amount}. Payment ID: {payment_id}."
    print(f"Notification sent to user {user_id}: {notification_message}")  # Mock notification

    # Step 5: Log transaction via RabbitMQ (mocked for simplicity)
    transaction_log = {
        "userId": user_id,
        "cardId": card_id,
        "amount": amount,
        "paymentId": payment_id,
        "status": payment_status
    }
    print(f"Transaction logged: {transaction_log}")  # Mock transaction log

    # Step 6: Fetch updated balance using Check Balance service
    try:
        updated_response = requests.get(check_balance_url.format(user_id=user_id))
        if updated_response.status_code == 200:
            updated_balance_data = updated_response.json()
            return jsonify({
                "code": 200,
                "message": "Top-up successful",
                "data": updated_balance_data["data"]
            }), 200
        else:
            return jsonify({"code": 500, "message": "Failed to fetch updated balance"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error fetching updated balance: {str(e)}"}), 500


if __name__ == "__main__":
    print("Starting Top-Up Service...")
    app.run(host="0.0.0.0", port=5007, debug=True)