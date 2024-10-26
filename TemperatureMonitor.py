import pika
import json

EXCHANGE_NAME = 'health_exchange'

def callback(ch, method, properties, body):
    message = json.loads(body)
    temperature = message["temperature"]
    print(" [x] Recebido temperatura:", message)
    if temperature < 36.0 or temperature > 37.5:
        print(" [!] Atenção: Temperatura fora do normal:", temperature)

def consume_temperature():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')
    queue_name = channel.queue_declare(queue='', exclusive=True).method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key="health.temperature")

    print(" [*] Aguardando temperatura corporal...")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    consume_temperature()
