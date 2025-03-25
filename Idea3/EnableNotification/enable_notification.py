from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os
import time
import threading
from datetime import datetime
import amqp_lib
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URL for SelectedRoute microservice
selected_route_URL = "http://selected_route:5301/selectedroute"

# URL for BusTracking microservice
bus_tracking_URL = "http://bus_tracking:5030/bus-tracking"

# RabbitMQ Configuration
rabbit_host = "G6T6-rabbit"
rabbit_port = 5672
notification_exchange = "notification.direct"
notification_exchange_type = "direct"
notification_routing_key = "notification"

# Global connection variables
connection = None
channel = None

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

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    global connection
    global channel
    
    print(" Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=notification_exchange,
            exchange_type=notification_exchange_type
        )
    except Exception as exception:
        print(f" Unable to connect to RabbitMQ.\n {exception=}\n")
        exit(1)  # terminate

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
        print("Notification Sent!")
        return True, notification_data
    
    return False, None

def publish_notification(notification_data):
    """Publish notification to RabbitMQ"""
    try:
        # Ensure AMQP connection is established
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
            
        channel.basic_publish(
            exchange=notification_exchange,
            routing_key=notification_routing_key,
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

def track_bus_arrival(bus_stop_code, bus_id):
    """Background task to track bus arrival and send notification"""
    should_notify = False
    notification_data = None
    
    while not should_notify:
        # Process bus arrival information
        should_notify, notification_data = process_bus_arrival(bus_stop_code, bus_id)
        
        # If bus is arriving in less than 2 minutes, publish notification
        if should_notify and notification_data:
            # Publish notification
            publish_notification(notification_data)
            print(f"Notification sent!", flush=True)
            break
        else:
            # Wait for 2 minutes before checking again
            print(f"Bus not arriving soon, checking again in 2 minutes", flush=True)
            time.sleep(120)  # Wait for 2 minutes

@app.route("/enable_notification/<int:RouteID>", methods=["GET"])
def enable_notification(RouteID):
    try:
        print(f"\nReceived request to enable notification for RouteID: {RouteID}")
        
        # Process the request
        result = process_notification_request(RouteID)
        return jsonify(result), result["code"]
        
    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print("Error: {}".format(ex_str))
        
        return jsonify({
            "code": 500,
            "message": "enable_notification.py internal error:",
            "exception": ex_str
        }), 500

def process_notification_request(RouteID):
    # 1. Invoke the SelectedRoute microservice to get BusStopCode and BusID
    print(" Invoking SelectedRoute microservice...")
    selected_route_result = invoke_http(
        f"{selected_route_URL}/{RouteID}", 
        method="GET"
    )
    print(f" selected_route_result: {selected_route_result}\n")
    
    # 2. Check the result from SelectedRoute
    code = selected_route_result["code"]
    if code not in range(200, 300):
        return {
            "code": 404,
            "data": {"selected_route_result": selected_route_result},
            "message": "Selected route not found."
        }
    
    # 3. Extract BusStopCode and BusID from the response
    route_data = selected_route_result["data"]
    bus_stop_code = route_data["BusStopCode"]
    bus_id = route_data["BusID"]
    
    # 4. Start tracking the bus in a separate thread
    tracking_thread = threading.Thread(
        target=track_bus_arrival,
        args=(bus_stop_code, bus_id)
    )
    tracking_thread.daemon = True
    tracking_thread.start()
    
    # 5. Return immediate success response
    return {
        "code": 201,
        "data": {
            "RouteID": RouteID,
            "BusStopCode": bus_stop_code,
            "BusID": bus_id,
            "tracking_started": True
        },
        "message": "Notification enabled successfully. You will be notified when the bus is arriving."
    }

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for enabling notifications...")
    connectAMQP()
    app.run(host="0.0.0.0", port=5302, debug=True)
