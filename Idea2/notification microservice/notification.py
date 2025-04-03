from flask import Flask, request, jsonify
from twilio.rest import Client
import os
from dotenv import load_dotenv
import amqp_lib
import pika
from threading import Thread
import json
import datetime

load_dotenv()

rabbit_host = "G6T6-rabbit"
rabbit_port = 5672
exchange_name = "SmartTransport"
exchange_type = "direct"

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def start_consumer():
    try:
        # Declare exchange and queue before consuming
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
            queue_name="Notification",
            routing_key="notification",  # Add binding key
            durable=True  # For persistent messages
        )
        
        # Start consuming with proper ack handling
        channel.basic_consume(
            queue="Notification",
            on_message_callback=handle_notification_message,
            auto_ack=False
        )
        print(" [*] Waiting for notifications")
        channel.start_consuming()
    except Exception as e:
        print(f"Consumer failed: {str(e)}")

def handle_notification_message(channel, method, properties, body):
    try:
        data = json.loads(body)
        success = send_notification({
            "recipient": data.get('phone_number'),
            "message": f"Payment of SGD{data['amount']/100:.2f} succeeded"
        })
        if success:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        channel.basic_nack(delivery_tag=method.delivery_tag)

# @app.route('/notify', methods=['POST'])
def send_notification(data):
    try:
        # Removed Flask route decorator
        twilio_client.messages.create(
            body=data['message'],
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=data['recipient']
        )
        return True
    except Exception as e:
        print(f"Notification failed: {str(e)}")
        return False

if __name__ == "__main__":
    Thread(target=start_consumer, daemon=True).start()
    app.run(host='0.0.0.0', port=5210, debug=False)
