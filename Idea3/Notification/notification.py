import os
import json
import sys
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import amqp_lib

# RabbitMQ Configuration
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "notification.direct"
exchange_type = "direct"
queue_name = "Notification"
routing_key = "notification"

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = ""  # Change to your verified sender
TO_EMAIL = ""  # Change to your recipient

def send_email(subject, content, to_email=TO_EMAIL):
    """Send email using SendGrid API"""
    try:
        # Initialize SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Create email components
        from_email = Email(FROM_EMAIL)
        to_email = To(to_email)
        content = Content("text/plain", content)
        
        # Create mail object
        mail = Mail(from_email, to_email, subject, content)
        
        # Get JSON representation
        mail_json = mail.get()
        
        # Send HTTP POST request to SendGrid API
        response = sg.client.mail.send.post(request_body=mail_json)
        
        print(f"Email sent successfully! Status code: {response.status_code}")
        print(f"Headers: {response.headers}")
        return True
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def callback(ch, method, properties, body):
    """Process messages from notification queue"""
    try:
        # Parse the message
        notification = json.loads(body)
        print(f"Received notification: {notification}")
        
        # Extract bus information
        bus_stop_code = notification.get('BusStopCode')
        service_no = notification.get('ServiceNo')
        minutes = notification.get('MinutesToArrival')
        
        if not all([bus_stop_code, service_no, minutes is not None]):
            print("Missing required notification data")
            return
        
        # Create email subject and content
        subject = f"Bus Arrival Alert: Service {service_no}"
        content = (
            f"Your bus {service_no} is arriving at bus stop {bus_stop_code} "
            f"in {minutes:.1f} minutes!\n\n"
            f"Please proceed to the bus stop now."
        )
        
        # Send email notification
        send_email(subject, content)
        
    except json.JSONDecodeError:
        print("Invalid JSON in notification message")
    except Exception as e:
        print(f"Error processing notification: {str(e)}")

def start_consumer():
    """Start consuming messages from the notification queue"""
    try:
        print("Starting notification consumer...")
        amqp_lib.start_consuming(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
            queue_name=queue_name,
            routing_key=routing_key,
            callback=callback
        )
    except Exception as e:
        print(f"Error starting consumer: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if SendGrid API key is set
    if not SENDGRID_API_KEY:
        print("Error: SENDGRID_API_KEY environment variable not set")
        print("Please set it using: export SENDGRID_API_KEY='your_api_key'")
        sys.exit(1)
    
    print("Starting Notification Microservice...")
    print(f"Listening for messages on exchange: {exchange_name}, queue: {queue_name}")
    
    # Start consuming messages
    start_consumer()
