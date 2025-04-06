from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import json
import pika
import threading
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# RabbitMQ Configuration
rabbit_host = "rabbitmq"
rabbit_port = 5672
notification_exchange = "notification.direct"
notification_exchange_type = "direct"
notification_queue = "bus_notification"
notification_routing_key = "bus_notification"

smart_transport_exchange = "SmartTransport"
smart_transport_exchange_type = "direct"
smart_transport_queue = "Notification"
smart_transport_routing_key = "notification"

def send_sms(phone_number, message):
    """Send SMS notification using Twilio"""
    try:
        # Ensure phone number is in proper format
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
            
        # Send message
        message = twilio_client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=phone_number
        )
        
        print(f"SMS sent to {phone_number}, SID: {message.sid}")
        return True, message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False, str(e)

def bus_notification_callback(ch, method, properties, body):
    """Process messages from bus notification queue"""
    try:
        # Parse the message
        notification = json.loads(body)
        print(f"Received bus notification: {notification}")
        
        # Extract phone number and notification details
        phone_number = notification.get('PhoneNumber')
        bus_service = notification.get('ServiceNo')
        bus_stop = notification.get('BusStopCode')
        minutes = notification.get('MinutesToArrival')
        
        if not all([phone_number, bus_service, bus_stop, minutes is not None]):
            print("Missing required notification data")
            return
        
        # Create notification message
        message = (
            f"Your bus {bus_service} is arriving at bus stop {bus_stop} "
            f"in {minutes:.1f} minutes! Please proceed to the bus stop now."
        )
        
        # Send SMS notification
        success, result = send_sms(phone_number, message)
        
        if success:
            print(f"Notification sent successfully to {phone_number}")
        else:
            print(f"Failed to send notification: {result}")
            
    except json.JSONDecodeError:
        print("Invalid JSON in notification message")
    except Exception as e:
        print(f"Error processing notification: {str(e)}")

def smart_transport_callback(ch, method, properties, body):
    """Process incoming SmartTransport messages"""
    try:
        data = json.loads(body)
        print(f"Received SmartTransport notification: {data}")
        
        # Extract values safely
        recipient = data.get('recipient')
        message = data.get('message')
        
        if not all([recipient, message]):
            raise ValueError("Invalid message format")
            
        # Add country code if missing
        if not recipient.startswith("+"):
            recipient = f"+65{recipient}"
            
        # Send notification
        success, _ = send_sms(recipient, message)
        
        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_bus_notification_consumer():
    """Start consuming messages from the bus notification queue"""
    try:
        print("Starting bus notification consumer...")
        
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port,
                heartbeat=300,
                blocked_connection_timeout=300
            )
        )
        
        channel = connection.channel()
        
        # Declare exchange and queue
        channel.exchange_declare(
            exchange=notification_exchange,
            exchange_type=notification_exchange_type,
            durable=True
        )
        
        channel.queue_declare(
            queue=notification_queue,
            durable=True
        )
        
        channel.queue_bind(
            exchange=notification_exchange,
            queue=notification_queue,
            routing_key=notification_routing_key
        )
        
        # Set up consumer
        channel.basic_consume(
            queue=notification_queue,
            on_message_callback=bus_notification_callback,
            auto_ack=True
        )
        
        print(f"Waiting for messages on queue: {notification_queue}")
        channel.start_consuming()
        
    except Exception as e:
        print(f"Error starting bus notification consumer: {str(e)}")

def start_smart_transport_consumer():
    """Start consuming messages from the SmartTransport queue"""
    try:
        print("Starting SmartTransport consumer...")
        
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port,
                heartbeat=300,
                blocked_connection_timeout=300
            )
        )
        
        channel = connection.channel()
        
        # Declare exchange and queue
        channel.exchange_declare(
            exchange=smart_transport_exchange,
            exchange_type=smart_transport_exchange_type,
            durable=True
        )
        
        channel.queue_declare(
            queue=smart_transport_queue,
            durable=True
        )
        
        channel.queue_bind(
            exchange=smart_transport_exchange,
            queue=smart_transport_queue,
            routing_key=smart_transport_routing_key
        )
        
        # Set up consumer
        channel.basic_consume(
            queue=smart_transport_queue,
            on_message_callback=smart_transport_callback,
            auto_ack=False
        )
        
        print(f"Waiting for messages on queue: {smart_transport_queue}")
        channel.start_consuming()
        
    except Exception as e:
        print(f"Error starting SmartTransport consumer: {str(e)}")

def send_notification():
    """Endpoint for sending notifications via SMS/WhatsApp"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['message', 'recipient']):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Extract parameters with defaults
        message = data['message']
        recipient = data['recipient']
        channel = data.get('channel', 'sms')  # Default to SMS
        
        # Determine sender based on channel
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        if channel == "whatsapp":
            from_number = f"whatsapp:{from_number}"
            recipient = f"whatsapp:{recipient}"
        
        # Send message
        message = twilio_client.messages.create(
            body=message,
            from_=from_number,
            to=recipient
        )
        
        return jsonify({
            "status": "queued",
            "sid": message.sid
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    # Start the consumers in separate threads
    bus_thread = threading.Thread(target=start_bus_notification_consumer)
    bus_thread.daemon = True
    bus_thread.start()
    
    smart_thread = threading.Thread(target=start_smart_transport_consumer)
    smart_thread.daemon = True
    smart_thread.start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5210, debug=True)
