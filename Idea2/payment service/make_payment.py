import os
import stripe
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

@app.route('/makepayment', methods=['POST'])
def MakePayment():
    data = request.get_json()
    amount = data.get('amount')

    try:
        # Create a PaymentIntent with the order amount and currency
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='sgd',
        )
        return jsonify({
            'clientSecret': payment_intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    print("Composite service: Make Payment ...")
    app.run(host='0.0.0.0', port=5208, debug=True)