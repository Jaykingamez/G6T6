#!/usr/bin/env python3
"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika
import time

# Configuration
amqp_host = "rabbitmq"
amqp_port = 5672

# Exchange and queue configurations
exchanges_and_queues = [
    {
        "exchange_name": "notification.direct",
        "exchange_type": "direct",
        "queue_name": "bus_notification",
        "routing_key": "bus_notification"
    },
    {
        "exchange_name": "SmartTransport",
        "exchange_type": "direct",
        "queue_name": "Notification",
        "routing_key": "notification"
    },
    {
        "exchange_name": "NotifyMe",
        "exchange_type": "direct",
        "queue_name": "NotifyMe",
        "routing_key": "notify_me"
    }
]

def create_connection_with_retry(hostname, port, max_retries=12, retry_interval=5):
    """Retry connection to RabbitMQ until it succeeds or max retries are reached."""
    retries = 0
    while retries < max_retries:
        try:
            print(f"Connecting to AMQP broker {hostname}:{port}... (Attempt {retries + 1}/{max_retries})")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=hostname,
                    port=port,
                    heartbeat=300,
                    blocked_connection_timeout=300,
                )
            )
            print("Connected")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}. Retrying in {retry_interval} seconds...")
            retries += 1
            time.sleep(retry_interval)
    raise Exception("Failed to connect to RabbitMQ after maximum retries.")

def setup_exchanges_and_queues(connection, configurations):
    """Set up exchanges and queues based on provided configurations."""
    channel = connection.channel()
    
    for config in configurations:
        # Declare exchange
        print(f"Declaring exchange: {config['exchange_name']}")
        channel.exchange_declare(
            exchange=config['exchange_name'],
            exchange_type=config['exchange_type'],
            durable=True
        )
        
        # Declare queue
        print(f"Declaring queue: {config['queue_name']}")
        channel.queue_declare(queue=config['queue_name'], durable=True)
        
        # Bind queue to exchange with routing key
        print(f"Binding queue {config['queue_name']} to exchange {config['exchange_name']} with routing key {config['routing_key']}")
        channel.queue_bind(
            exchange=config['exchange_name'],
            queue=config['queue_name'],
            routing_key=config['routing_key']
        )

# Main execution flow
try:
    # Create connection with retry logic
    connection = create_connection_with_retry(amqp_host, amqp_port)
    
    # Set up exchanges and queues
    setup_exchanges_and_queues(connection, exchanges_and_queues)
    
    # Close connection
    print("Closing connection...")
    connection.close()
    print("Setup completed successfully!")
except Exception as e:
    print(f"Error setting up RabbitMQ: {e}")
