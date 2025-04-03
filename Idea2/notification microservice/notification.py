from flask import Flask, request, jsonify
from twilio.rest import Client
import os
from dotenv import load_dotenv
import amqp_lib
import json

load_dotenv()

# RabbitMQ Configuration
rabbit_host = "rabbitmq"  # Use Docker service name
rabbit_port = 5672
exchange_name = "SmartTransport"
exchange_type = "direct"
queue_name = "Notification"

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def callback(channel, method, properties, body):
    """Process incoming RabbitMQ messages"""
    try:
        data = json.loads(body)
        print(f"Received notification: {data}")
        
        # Extract values safely
        recipient = data.get('recipient')
        message = data.get('message')
        
        if not all([recipient, message]):
            raise ValueError("Invalid message format")
            
        # Add country code if missing
        if not recipient.startswith("+"):
            recipient = f"+65{recipient}"
            
        # Send notification
        success = send_notification({
            "recipient": recipient,
            "message": message
        })
        
        if success:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def send_notification(data):
    """Send SMS using Twilio"""
    try:
        # Validate required fields
        if not all(key in data for key in ['recipient', 'message']):
            raise ValueError("Missing required fields in notification data")
            
        # Format phone number
        recipient = data['recipient'].replace(" ", "").replace("-", "")
        
        twilio_client.messages.create(
            body=data['message'],
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=recipient
        )
        print(f"Notification sent to {recipient}")
        return True
    except Exception as e:
        print(f"Notification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"Starting notification service...")
    try:
        amqp_lib.start_consuming(
            rabbit_host,
            rabbit_port,
            exchange_name,
            exchange_type,
            queue_name,
            callback,
        )
    except Exception as e:
        print(f"Failed to start consumer: {str(e)}")
