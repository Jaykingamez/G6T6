from flask import Flask, request, jsonify
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

@app.route('/notify', methods=['POST'])
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
    app.run(host='0.0.0.0', port=5210, debug=True)
