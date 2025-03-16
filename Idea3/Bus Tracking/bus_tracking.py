import json
import os
import sys
import time
import requests
from datetime import datetime
import amqp_lib
import pika
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# RabbitMQ Configuration for Subscription
RABBIT_HOST = "localhost"
RABBIT_PORT = 5672
TRACKING_EXCHANGE = "tracking_direct"
TRACKING_EXCHANGE_TYPE = "direct"
TRACKING_QUEUE = "Tracking"
TRACKING_ROUTING_KEY = "tracking"

# RabbitMQ Configuration for Publishing
NOTIFICATION_EXCHANGE = "notification.direct"
NOTIFICATION_EXCHANGE_TYPE = "direct"
NOTIFICATION_ROUTING_KEY = "notification"

# LTA API Configuration
LTA_API_URL = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
LTA_API_KEY = os.environ.get("LTA_API_KEY", "your_api_key_here")

def calculate_arrival_time(estimated_arrival):
    """Calculate minutes until bus arrival"""
    try:
        # Parse the estimated arrival time from the API
        arrival_time = datetime.fromisoformat(estimated_arrival.replace('Z', '+00:00'))
        
        # Get current time
        current_time = datetime.now().astimezone()
        
        # Calculate time difference in minutes
        time_diff = (arrival_time - current_time).total_seconds() / 60
        
        return max(0, time_diff)  # Ensure we don't return negative minutes
    except Exception as e:
        print(f"Error calculating arrival time: {e}")
        return None

def get_bus_arrival_info(bus_stop_code, service_no):
    """Call LTA API to get bus arrival information"""
    headers = {
        'AccountKey': LTA_API_KEY,
        'accept': 'application/json'
    }
    
    params = {
        'BusStopCode': bus_stop_code,
        'ServiceNo': service_no
    }
    
    try:
        response = requests.get(LTA_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling LTA API: {e}")
        return None

def process_bus_arrival(bus_stop_code, service_no):
    """Process bus arrival information and check if notification should be sent"""
    arrival_data = get_bus_arrival_info(bus_stop_code, service_no)
    
    if not arrival_data or 'Services' not in arrival_data or not arrival_data['Services']:
        print(f"No data found for bus {service_no} at stop {bus_stop_code}")
        return False, None
    
    # Extract the first service that matches our criteria
    service = arrival_data['Services'][0]
    
    # Check the next bus arrival time
    next_bus = service.get('NextBus', {})
    estimated_arrival = next_bus.get('EstimatedArrival', '')
    
    if not estimated_arrival:
        print(f"No estimated arrival time for bus {service_no}")
        return False, None
    
    # Calculate minutes until arrival
    minutes_to_arrival = calculate_arrival_time(estimated_arrival)
    
    if minutes_to_arrival is None:
        return False, None
    
    print(f"Bus {service_no} arriving at stop {bus_stop_code} in {minutes_to_arrival:.1f} minutes")
    
    # Check if bus is arriving in less than 2 minutes
    if minutes_to_arrival <= 2:
        # Prepare notification data
        notification_data = {
            'BusStopCode': bus_stop_code,
            'ServiceNo': service_no,
            'EstimatedArrival': estimated_arrival,
            'MinutesToArrival': minutes_to_arrival,
            'Load': next_bus.get('Load', ''),
            'Feature': next_bus.get('Feature', ''),
            'Type': next_bus.get('Type', '')
        }
        return True, notification_data
    
    return False, None

def publish_notification(channel, notification_data):
    """Publish notification to RabbitMQ"""
    try:
        channel.basic_publish(
            exchange=NOTIFICATION_EXCHANGE,
            routing_key=NOTIFICATION_ROUTING_KEY,
            body=json.dumps(notification_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        print(f"Published notification for bus {notification_data['ServiceNo']} arriving at stop {notification_data['BusStopCode']}")
        return True
    except Exception as e:
        print(f"Error publishing notification: {e}")
        return False

def callback(ch, method, properties, body):
    """Callback function for processing messages from the tracking queue"""
    try:
        # Parse the message
        message = json.loads(body)
        bus_stop_code = message.get('BusStopCode')
        service_no = message.get('BusID')
        
        if not bus_stop_code or not service_no:
            print("Missing required parameters in message")
            return
        
        print(f"Processing request for bus {service_no} at stop {bus_stop_code}")
        
        # Keep checking until bus arrival time is less than 2 minutes
        should_notify = False
        notification_data = None
        
        while not should_notify:
            # Process bus arrival information
            should_notify, notification_data = process_bus_arrival(bus_stop_code, service_no)
            
            # If bus is arriving in less than 2 minutes, publish notification
            if should_notify and notification_data:
                # Connect to notification exchange
                notification_connection, notification_channel = amqp_lib.connect(
                    hostname=RABBIT_HOST,
                    port=RABBIT_PORT,
                    exchange_name=NOTIFICATION_EXCHANGE,
                    exchange_type=NOTIFICATION_EXCHANGE_TYPE
                )
                
                # Publish notification
                publish_notification(notification_channel, notification_data)
                
                # Close connection
                amqp_lib.close(notification_connection, notification_channel)
                break
            else:
                # Wait for 2 minutes before checking again
                print(f"Bus not arriving soon, checking again in 2 minutes")
                time.sleep(120)  # Wait for 2 minutes
    
    except json.JSONDecodeError:
        print("Invalid JSON in message")
    except Exception as e:
        print(f"Error processing message: {e}")

def start_consumer():
    """Start consuming messages from the tracking queue"""
    try:
        amqp_lib.start_consuming(
            hostname=RABBIT_HOST,
            port=RABBIT_PORT,
            exchange_name=TRACKING_EXCHANGE,
            exchange_type=TRACKING_EXCHANGE_TYPE,
            queue_name=TRACKING_QUEUE,
            callback=callback
        )
    except Exception as e:
        print(f"Error starting consumer: {e}")
        sys.exit(1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "BusTracking"}), 200

@app.route('/track', methods=['POST'])
def track_bus():
    """Endpoint to manually track a bus"""
    data = request.get_json()
    
    bus_stop_code = data.get('BusStopCode')
    service_no = data.get('BusID')
    
    if not bus_stop_code or not service_no:
        return jsonify({"error": "Missing required parameters"}), 400
    
    should_notify, notification_data = process_bus_arrival(bus_stop_code, service_no)
    
    if notification_data:
        return jsonify(notification_data), 200
    else:
        return jsonify({"message": "Bus not arriving soon"}), 200

if __name__ == '__main__':
    # Start the consumer in a separate thread
    import threading
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5002, debug=True)
