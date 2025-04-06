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
    try:
        # Get the current datetime
        current_datetime = datetime.datetime.utcnow()
        formatted_datetime = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        # For new cards, ensure previous balance is 0.1
        prev_balance_decimal = Decimal('0.1') if prevBalance is None or prevBalance == 0 else Decimal(str(prevBalance))

        # Convert amount from cents to dollars
        try:
            amount_decimal = Decimal(amount) / 100
        except (TypeError, ValueError):
            app.logger.error(f"Invalid amount value: {amount}")
            return {
                "code": 400,
                "message": "Invalid amount format"
            }

        new_balance_decimal = prev_balance_decimal + amount_decimal

        # Generate a 16-digit transaction ID
        transaction_id = str(int(datetime.datetime.now().timestamp() * 1000000))  # Using microseconds for more digits
        while len(transaction_id) < 16:  # Pad with extra digits if needed
            transaction_id += str(int(datetime.datetime.now().microsecond))
        transaction_id = transaction_id[:16]  # Take first 16 digits

        # Format payload exactly as per API documentation with numeric values
        payload = {
            "TransactionId": transaction_id,
            "UserId": int(user_id),  # Convert to integer
            "CardId": int(card_id),  # Convert to integer
            "Amount": float(amount_decimal),  # Convert to float as shown in API example
            "PreviousBalance": 0.1 if prev_balance_decimal == Decimal('0.1') else float(prev_balance_decimal),  # 0.1 for new cards
            "NewBalance": float(new_balance_decimal),  # Convert to float as shown in API example
            "CreatedAt": formatted_datetime
        }

        app.logger.info(f"Sending transaction to Outsystems with payload: {payload}")
        
        # Add retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.post(
                    create_transaction_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=10
                )

                # Log the complete response for debugging
                app.logger.info(f"Outsystems response: Status={response.status_code}, Body={response.text}")

                if response.status_code == 200:  # API doc shows 200 is the success code
                    response_data = response.json()
                    # Check for empty status and message as shown in API doc
                    if "Status" in response_data and "Message" in response_data:
                        return {
                            "code": 200,
                            "data": response_data
                        }
                    
                elif response.status_code >= 500:  # Server error, retry
                    retry_count += 1
                    if retry_count < max_retries:
                        app.logger.warning(f"Retrying transaction creation (attempt {retry_count + 1}/{max_retries})")
                        continue
                
                # If we get here, either we've exhausted retries or got a 4xx error
                error_msg = f"Outsystems API error: Status {response.status_code}, Response: {response.text}"
                app.logger.error(error_msg)
                return {
                    "code": response.status_code,
                    "message": error_msg,
                    "payload": payload  # Include payload in error response for debugging
                }

            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count < max_retries:
                    app.logger.warning(f"Network error, retrying (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                    continue
                error_msg = f"Error connecting to Outsystems after {max_retries} attempts: {str(e)}"
                app.logger.error(error_msg)
                return {
                    "code": 500,
                    "message": error_msg
                }

    except Exception as e:
        error_msg = f"Unexpected error in create_transaction_in_outsystems: {str(e)}"
        app.logger.error(error_msg)
        return {
            "code": 500,
            "message": error_msg
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
                    'unit_amount': str(Decimal(data["amount"]) / 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:5208/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://localhost:8080/profile',
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
                return redirect('http://localhost:8080/profile?status=error&message=Failed+to+update+card+balance')

            # 2. Send notification via AMQP
            notification_sent = send_payment_notification(
                recipient=metadata['phone_number'],
                message=f"Top-up of SGD{session.amount_total/100:.2f} succeeded"
            )
            if not notification_sent:
                app.logger.warning("Failed to send notification, but continuing with transaction")

            # Check if Balance exists in metadata - if not, this is a new card
            is_new_card = 'Balance' not in metadata or not metadata['Balance']
            previous_balance = Decimal('0.1') if is_new_card else Decimal(metadata['Balance'])

            # 3. Create transaction via HTTP POST
            transaction_response = create_transaction_in_outsystems(
                user_id=metadata['user_id'],
                card_id=metadata['card_id'],
                amount=session.amount_total,
                prevBalance=previous_balance  # Will be 0.1 for new cards
            )

            if transaction_response.get('code') and transaction_response['code'] not in [200, 201]:
                app.logger.error(f"Failed to create transaction: {transaction_response}")
                # Even if transaction creation fails, we've already updated the balance
                return redirect('http://localhost:8080/profile?status=warning&message=Balance+updated+but+transaction+record+failed')

            # 4. Get updated balance
            balance_response = check_balance(metadata['user_id'])
            if 'error' in balance_response:
                app.logger.error(f"Failed to fetch updated balance: {balance_response['error']}")
            else:
                app.logger.info(f"Updated balance: {balance_response}")
            
            success_url = (
                f'http://localhost:8080/profile?'
                f'status=success&'
                f'amount={session.amount_total/100:.2f}&'
                f'message=Payment+successful'
            )
            return redirect(success_url)

        else:
            return redirect('http://localhost:8080/profile?status=failed&message=Payment+was+not+successful')

    except Exception as e:
        app.logger.error(f"Error in success handler: {str(e)}")
        return redirect(f'http://localhost:8080/profile?status=error&message=Unexpected+error+occurred')
    

if __name__ == "__main__":
    print("Composite service: Make Payment ...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5208, debug=True)