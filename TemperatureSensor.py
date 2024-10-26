import pika
import json
import random
import time

EXCHANGE_NAME = 'health_exchange'

def publish_temperature():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

    while True:
        temperature = round(35 + (40 - 35) * random.random(), 2)
        message = json.dumps({"device_id": 2, "temperature": temperature})
        channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="health.temperature", body=message)
        print(" [x] Enviou temperatura corporal:", message)
        time.sleep(5)

    connection.close()

if __name__ == "__main__":
    publish_temperature()
