import os
import stripe
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
# Set your secret key. Remember to switch to your live secret key in production!
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

app = Flask(__name__)
CORS(app, supports_credentials=True)

check_balance_url = "http://localhost:5005/checkbalance/<int:user_id>"
send_notification_url = "http://localhost:5210/notify"
user_url = "http://localhost:5201/users"
create_transaction_url="https://personal-tkjmxw54.outsystemscloud.com/TransactionManagement/rest/TransactionsAPI/CreateTransaction"
card_url="http://localhost:5203/cards"


def send_payment_notification(recipient, message, channel="sms"):
    """Helper function to send payment notifications"""
    try:
        response = requests.post(
            send_notification_url,
            json={
                "message": message,
                "recipient": recipient,
                "channel": channel
            },
            timeout=5  # 5-second timeout
        )
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Notification failed: {str(e)}")
        return False

@app.route('/makepayment', methods=['POST'])
def MakePayment():
    data = request.get_json()
    amount = data.get('amount')
    phone_number = data.get('phone_number')  # Get from request

    try:
        # Create a PaymentIntent with the order amount and currency
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='sgd',
        )

        # Send initial notification
        notification_sent = send_payment_notification(
            recipient=phone_number,
            message=f"Payment of SGD{amount/100:.2f} is being processed"
        )
        
    
        return jsonify({
            'clientSecret': payment_intent['client_secret']
        })
    
        
    except Exception as e:
        return jsonify(error=str(e)), 500
    

if __name__ == "__main__":
    print("Composite service: Make Payment ...")
    app.run(host='0.0.0.0', port=5208, debug=True)