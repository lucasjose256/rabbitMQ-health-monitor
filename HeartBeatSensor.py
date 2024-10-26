import pika
import json
import random
import time

EXCHANGE_NAME = 'health_exchange'

def publish_heartbeat():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

    while True:
        heartbeat = random.randint(50, 150)
        message = json.dumps({"device_id": 1, "heartbeat": heartbeat})
        channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="health.heartbeat", body=message)
        print(" [x] Enviou batimentos cardíacos:", message)
        time.sleep(5)

    connection.close()

if __name__ == "__main__":
    publish_heartbeat()
