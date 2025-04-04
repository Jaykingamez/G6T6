import os
import stripe
import json
import pika
import requests
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import amqp_lib
from decimal import Decimal
import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
# Set your secret key. Remember to switch to your live secret key in production!
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/makepayment": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

check_balance_url = "http://check_balance:5205/checkbalance/{user_id}"
send_notification_url = "http://notification:5210"
user_url = "http://user:5201/users"
create_transaction_url="https://personal-tkjmxw54.outsystemscloud.com/TransactionManagement/rest/TransactionsAPI/CreateTransaction"
update_card_balance_url = "http://card:5203/cards/{card_id}/balance"  # PATCH endpoint for card balance update

# RabbitMQ
rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "SmartTransport"
exchange_type = "direct"
connection = None 
channel = None

def connectAMQP():
    global connection, channel
    print("Connecting to AMQP broker...")
    try:
        # Connect to RabbitMQ
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
        )

        # Declare queues and bindings
        channel.queue_declare(queue="Notification", durable=True)
        channel.queue_bind(
            exchange=exchange_name,
            queue="Notification",
            routing_key="notification"
        )
        print("[AMQP] Connected successfully")
    except Exception as e:
        print(f"AMQP Connection Failed: {str(e)}")
        exit(1)

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

def send_payment_notification(recipient, message, notification_type="sms"):
    notification_data = {
        "recipient": recipient,
        "message": message
    }
    try:    
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
            
        channel.basic_publish(
            exchange=exchange_name,
            routing_key="notification",
            body=json.dumps(notification_data),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )
        return True
    except Exception as e:
        app.logger.error(f"Notification publish failed: {str(e)}")
        return False

def create_transaction_in_outsystems(user_id, card_id, amount, prevBalance):
    """Create transaction in Outsystems via HTTP POST"""
    # Get the current datetime
    current_datetime = datetime.datetime.utcnow()
    formatted_datetime = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z' 

    amount_decimal = Decimal(amount) / 100  # Convert cents to dollars
    prev_balance_decimal = Decimal(prevBalance)
    new_balance_decimal = prev_balance_decimal + amount_decimal

    payload = {
        "UserId": user_id,
        "CardId": card_id,
        "Amount": str(amount_decimal),
        "PreviousBalance": float(prev_balance_decimal),
        "NewBalance": float(new_balance_decimal),
        "CreatedAt": formatted_datetime
    }

    try:
        response = requests.post(
            create_transaction_url,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=10
        )


        if response:
            return response.json()

    except Exception as e:
        return {
            "code": 500,
            "message": f"Error connecting to Outsystems: {str(e)}"
        }

def update_card_balance(card_id, amount):
    """Call the PATCH endpoint to update the card balance."""
    try:
        response = requests.patch(
            update_card_balance_url.format(card_id=card_id),
            json={
                "operation": "add",  # Subtract payment amount from balance
                "amount": str(Decimal(amount) / 100)  # Convert cents to dollars
            },
            timeout=5  # Set a timeout for the request
        )
        return response.json() if response.status_code == 200 else {
            "code": response.status_code,
            "message": response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            "code": 500,
            "message": f"Failed to connect to card service: {str(e)}"
        }

@app.route('/makepayment', methods=['POST'])
def MakePayment():
    try:
        data = request.get_json()
        user_id = data.get('user_id')  # Add this line
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'sgd',
                    'product_data': {'name': f'Top-up for Card ID {data["card_id"]}'},
                    'unit_amount': data["amount"],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:5208/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://localhost:5208/cancel',
            metadata={
                'user_id': user_id,
                'card_id': data["card_id"],
                'phone_number': data["phone_number"],
                "Balance": str(Decimal(data.get("Balance", 0)))
            }
        )
        return jsonify({'checkout_url': session.url}), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
     
@app.route('/success', methods=['GET']) 
def handle_success():
    session_id = request.args.get('session_id')

    if not session_id:
        return jsonify(error="Missing session ID"), 400

    try:
        # Retrieve the Checkout Session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            metadata = session.metadata

            # 1. Update card balance
            update_response = update_card_balance(metadata['card_id'], session.amount_total)
            if update_response.get('code') != 200:
                app.logger.error(f"Failed to update card balance: {update_response['message']}")

             # 2. Send notification via AMQP
            send_payment_notification(
                recipient=metadata['phone_number'],
                message=f"Top-up of SGD{session.amount_total/100:.2f} succeeded"
            )

            # 3. Create transaction via HTTP POST
            create_transaction_in_outsystems(
                user_id=metadata['user_id'],
                card_id=metadata['card_id'],
                amount=session.amount_total,
                prevBalance=Decimal(metadata['Balance'])  # Convert to Decimal
            )

            # 4. Get updated balance
            balance_response = check_balance(metadata['user_id'])
            if 'error' in balance_response:
                app.logger.error(f"Failed to fetch updated balance: {balance_response['error']}")
            else:
                app.logger.info(f"Updated balance: {balance_response}")

            return jsonify({
                "status": "success",
                "new_balance": balance_response.get('data', {}).get('cards', [{}])[0].get('Balance')
            }), 200

        else:
            return jsonify({"status": "failed", "message": "Payment was not successful"}), 400

    except Exception as e:
        return jsonify(error=str(e)), 500
    

if __name__ == "__main__":
    print("Composite service: Make Payment ...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5208, debug=True)