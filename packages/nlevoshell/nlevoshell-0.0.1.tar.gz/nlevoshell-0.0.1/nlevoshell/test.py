import pika
import json
import time

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_user = 'evo'
rabbitmq_password = 'evo'

# RabbitMQ connection setup
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection_params = pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare the exchange (assuming it's a direct exchange, modify if necessary)
exchange_name = 'x.stb'
routing_key = 'req.stb.cmd'

# Construct the message
message = {
    "msg": "connect",
    "service": "backend",
    "action": "connect",
    "data": {
        "mode": "adb",
        "host": "192.168.219.50",
        "port": 5555,
        "username": "",
        "password": ""
    },
    "level": "info",
    "time": time.time()  # Get current timestamp
}


channel.basic_publish(
    exchange=exchange_name,
    routing_key=routing_key,
    body=json.dumps(message)
)

message = {
    "msg": "command",
    "service": "backend",
    "action": "connect",
    "data": {
        "mode": "adb/ssh",
        "command": "ls -alh"
    },
    "level": "info",
    "time": time.time()  # Get current timestamp
}


channel.basic_publish(
    exchange=exchange_name,
    routing_key=routing_key,
    body=json.dumps(message)
)

time.sleep(1)
channel.basic_publish(
    exchange=exchange_name,
    routing_key=routing_key,
    body=json.dumps(message)
)


print(f"Message sent to exchange {exchange_name} with routing key {routing_key}")

# Close the connection
connection.close()