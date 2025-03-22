#!/usr/bin/env python3
"""
A standalone script to create the notification exchange and queue on RabbitMQ.
"""

import pika

# Configuration
amqp_host = "localhost"
amqp_port = 5672

# Notification exchange configuration
notification_exchange_name = "notification.direct"
notification_exchange_type = "direct"
notification_queue = "Notification"
notification_routing_key = "notification"

def create_exchange(hostname, port, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    
    # connect to the broker
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    
    print("Connected")
    print("Open channel")
    channel = connection.channel()
    
    # Set up the exchange if the exchange doesn't exist
    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, 
        exchange_type=exchange_type, 
        durable=True
    )
    # 'durable' makes the exchange survive broker restarts
    
    return channel, connection

def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Declare queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts
    
    # bind the queue to the exchange via the routing_key
    print(f"Bind queue {queue_name} to exchange {exchange_name} with routing key {routing_key}")
    channel.queue_bind(
        exchange=exchange_name, 
        queue=queue_name, 
        routing_key=routing_key
    )

# Create notification exchange and queue
notification_channel, notification_connection = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name=notification_exchange_name,
    exchange_type=notification_exchange_type,
)

create_queue(
    channel=notification_channel,
    exchange_name=notification_exchange_name,
    queue_name=notification_queue,
    routing_key=notification_routing_key,
)

# Close connection
print("Closing connection...")
notification_connection.close()
print("Setup completed successfully!")
