from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os
import amqp_lib

app = Flask(__name__)
CORS(app)

# RabbitMQ Configuration
rabbit_host = "rabbitmq"
rabbit_port = 5672
notify_exchange = "NotifyMe"
notify_exchange_type = "direct"
notify_routing_key = "notify_me"

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
            exchange_name=notify_exchange,
            exchange_type=notify_exchange_type
        )
    except Exception as exception:
        print(f" Unable to connect to RabbitMQ.\n {exception=}\n")
        exit(1)  # terminate

def publish_to_notify_me(route_id):
    """Publish message to NotifyMe exchange"""
    try:
        # Ensure AMQP connection is established
        if connection is None or not amqp_lib.is_connection_open(connection):
            connectAMQP()
        
        # Prepare message data
        message_data = {
            'RouteID': route_id
        }
        
        channel.basic_publish(
            exchange=notify_exchange,
            routing_key=notify_routing_key,
            body=json.dumps(message_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        print(f"Published message to NotifyMe exchange for RouteID: {route_id}")
        return True
    except Exception as e:
        print(f"Error publishing message: {e}")
        return False

@app.route("/notify-me/<int:RouteID>", methods=["GET"])
def notify_me(RouteID):
    try:
        print(f"\nReceived request to start notification for RouteID: {RouteID}")
        
        # Publish message to NotifyMe exchange
        success = publish_to_notify_me(RouteID)
        
        if success:
            return jsonify({
                "code": 201,
                "data": {
                    "RouteID": RouteID
                },
                "message": "Notification request sent successfully. You will be notified when the bus is arriving."
            }), 201
        else:
            return jsonify({
                "code": 500,
                "message": "Failed to send notification request."
            }), 500
        
    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print("Error: {}".format(ex_str))
        
        return jsonify({
            "code": 500,
            "message": "notify_me_starter.py internal error:",
            "exception": ex_str
        }), 500

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is " + os.path.basename(__file__) + " for starting notifications...")
    connectAMQP()
    app.run(host='0.0.0.0', port=5302, debug=True)
