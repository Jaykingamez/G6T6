from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os
import amqp_lib
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# URL for SelectedRoute microservice
selected_route_URL = "http://localhost:5000/selectedroute"

# RabbitMQ Configuration
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "tracking_direct"
exchange_type = "direct"
routing_key = "tracking"

# Global connection variables
connection = None
channel = None

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    global connection
    global channel
    
    print(" Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type
        )
    except Exception as exception:
        print(f" Unable to connect to RabbitMQ.\n {exception=}\n")
        exit(1)  # terminate

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
    # Ensure AMQP connection is established
    if connection is None or not amqp_lib.is_connection_open(connection):
        connectAMQP()
    
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
    
    # 4. Prepare message for RabbitMQ
    tracking_data = {
        "BusStopCode": bus_stop_code,
        "BusID": bus_id
    }
    message = json.dumps(tracking_data)
    
    # 5. Publish the message to RabbitMQ
    print(f" Publishing message to exchange={exchange_name}, routing_key={routing_key}")
    print(f" Message: {message}")
    
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
    )
    
    # 6. Return success response
    return {
        "code": 201,
        "data": {
            "RouteID": RouteID,
            "BusStopCode": bus_stop_code,
            "BusID": bus_id
        },
        "message": "Notification enabled successfully."
    }

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for enabling notifications...")
    connectAMQP()
    app.run(host="0.0.0.0", port=5003, debug=True)
