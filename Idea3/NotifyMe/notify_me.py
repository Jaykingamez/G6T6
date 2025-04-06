from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os
import time
from datetime import datetime
import amqp_lib
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URL for SelectedRoute microservice
selected_route_URL = "http://selected_route:5301/selectedroute"

# URL for BusTracking microservice
bus_tracking_URL = "http://bus_tracking:5030/bus-tracking"

# URL for User microservice
user_URL = "http://user:5201/users"

# RabbitMQ Configuration for consuming
rabbit_host = "rabbitmq"
rabbit_port = 5672
consume_exchange = "NotifyMe"
consume_exchange_type = "direct"
consume_queue = "NotifyMe"
consume_routing_key = "notify_me"

# RabbitMQ Configuration for publishing
notification_exchange = "notification.direct"
notification_exchange_type = "direct"
notification_routing_key = "bus_notification"

# Global connection variables
connection = None
channel = None
consume_connection = None
consume_channel = None

def calculate_arrival_time(estimated_arrival):
    """Calculate minutes until bus arrival"""
    try:
        # Parse the estimated arrival time from the API
        arrival_time = datetime.fromisoformat(estimated_arrival.replace('Z', '+00:00'))
        
        # Get current time
        current_time = datetime.now().astimezone()
        
        # Calculate time difference in minutes
        time_diff = (arrival_time - current_time).total_seconds() / 60
        
        return max(0, time_diff) # Ensure we don't return negative minutes
    except Exception as e:
        print(f"Error calculating arrival time: {e}")
        return None

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    global connection
    global channel
    
    print(" Connecting to AMQP broker for publishing...")
    try:
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=notification_exchange,
            exchange_type=notification_exchange_type
        )
    except Exception as exception:
        print(f" Unable to connect to RabbitMQ.\n {exception=}\n")
        exit(1) # terminate

def connectConsumeAMQP():
    # Connect to RabbitMQ for consuming messages
    global consume_connection
    global consume_channel
    
    print(" Connecting to AMQP broker for consuming...")
    try:
        # Connect to RabbitMQ
        consume_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port,
                heartbeat=300,
                blocked_connection_timeout=300
            )
        )
        
        consume_channel = consume_connection.channel()
        
        # Declare exchange and queue
        consume_channel.exchange_declare(
            exchange=consume_exchange,
            exchange_type=consume_exchange_type,
            durable=True
        )
        
        consume_channel.queue_declare(
            queue=consume_queue,
            durable=True
        )
        
        consume_channel.queue_bind(
            exchange=consume_exchange,
            queue=consume_queue,
            routing_key=consume_routing_key
        )
        
        return True
    except Exception as e:
        print(f" Unable to connect to RabbitMQ for consuming.\n {e}\n")
        return False

def process_bus_arrival(bus_stop_code, service_no):
    """Process bus arrival information and check if notification should be sent"""
    # Call the BusTracking microservice to get bus arrival info
    params = {
        'BusStopCode': bus_stop_code,
        'ServiceNo': service_no
    }
    
    arrival_data = invoke_http(
        f"{bus_tracking_URL}",
        method="GET",
        params=params
    )
    
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

def publish_notification(notification_data, phone_number, route_name):
    """Publish notification to RabbitMQ with phone number and route name"""
    try:
        # Ensure AMQP connection is established
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        # Add phone number and route name to notification data
        notification_data['PhoneNumber'] = phone_number
        notification_data['RouteName'] = route_name
        
        channel.basic_publish(
            exchange=notification_exchange,
            routing_key=notification_routing_key,
            body=json.dumps(notification_data),
            properties=pika.BasicProperties(
                delivery_mode=2, # make message persistent
                content_type='application/json'
            )
        )
        print(f"Published notification for bus {notification_data['ServiceNo']} arriving at stop {notification_data['BusStopCode']} to phone {phone_number}")
        return True
    except Exception as e:
        print(f"Error publishing notification: {e}")
        return False

def process_notification_request(RouteID):
    try:
        # 1. Invoke the SelectedRoute microservice to get BusStopCode, BusID, UserID, and RouteName
        print(" Invoking SelectedRoute microservice...")
        selected_route_result = invoke_http(
            f"{selected_route_URL}/{RouteID}",
            method="GET"
        )
        print(f" selected_route_result: {selected_route_result}\n")
        
        # 2. Check the result from SelectedRoute
        code = selected_route_result["code"]
        if code not in range(200, 300):
            print(f"Selected route not found: {selected_route_result}")
            return
        
        # 3. Extract BusStopCode, BusID, UserID, and RouteName from the response
        route_data = selected_route_result["data"]
        bus_stop_code = route_data["BusStopCode"]
        bus_id = route_data["BusID"]
        user_id = route_data["UserID"]
        route_name = route_data["RouteName"]
        
        # 4. Get user phone number
        user_result = invoke_http(
            f"{user_URL}/{user_id}",
            method="GET"
        )
        
        if user_result["code"] != 200:
            print(f"Error retrieving user information: {user_result['message']}")
            return
        
        phone_number = user_result["data"]["Phone"]
        if not phone_number:
            print(f"User {user_id} does not have a phone number")
            return
        
        # 5. Process bus arrival and send notification
        should_notify = False
        notification_data = None
        
        while not should_notify:
            # Process bus arrival information
            should_notify, notification_data = process_bus_arrival(bus_stop_code, bus_id)
            
            # If bus is arriving in less than 2 minutes, publish notification
            if should_notify and notification_data:
                # Publish notification with phone number and route name
                publish_notification(notification_data, phone_number, route_name)
                print(f"Notification sent!", flush=True)
                break
            else:
                # Wait for 1 minute before checking again
                print(f"Bus not arriving soon, checking again in 1 minute", flush=True)
                time.sleep(60) # Wait for 1 minute
        
        print(f"Notification process completed for RouteID: {RouteID}")
    except Exception as e:
        print(f"Error processing notification request: {e}")

def callback(ch, method, properties, body):
    """Process messages from NotifyMe queue"""
    try:
        # Parse the message
        message = json.loads(body)
        print(f"Received message: {message}")
        
        # Extract RouteID from the message
        route_id = message.get('RouteID')
        
        if not route_id:
            print("Missing RouteID in message")
            return
        
        print(f"Processing notification request for RouteID: {route_id}")
        
        # Process the notification request
        process_notification_request(route_id)
        
    except json.JSONDecodeError:
        print("Invalid JSON in message")
    except Exception as e:
        print(f"Error processing message: {str(e)}")

def start_consumer():
    """Start consuming messages from the NotifyMe queue"""
    try:
        print("Starting NotifyMe consumer...")
        
        # Connect to RabbitMQ for consuming
        if not connectConsumeAMQP():
            print("Failed to connect to RabbitMQ for consuming")
            return
        
        # Set up consumer
        consume_channel.basic_consume(
            queue=consume_queue,
            on_message_callback=callback,
            auto_ack=True
        )
        
        print(f"Waiting for messages on queue: {consume_queue}")
        consume_channel.start_consuming()
        
    except Exception as e:
        print(f"Error starting consumer: {str(e)}")

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is " + os.path.basename(__file__) + " for enabling notifications...")
    connectAMQP()
    start_consumer()
