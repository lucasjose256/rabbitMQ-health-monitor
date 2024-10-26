import pika
import json

EXCHANGE_NAME = 'health_exchange'

def callback(ch, method, properties, body):
    message = json.loads(body)
    heartbeat = message["heartbeat"]
    print(" [x] Recebido batimentos cardíacos:", message)
    if heartbeat < 60 or heartbeat > 100:
        print(" [!] Atenção: Batimentos fora do normal:", heartbeat)

def consume_heartbeat():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')
    queue_name = channel.queue_declare(queue='', exclusive=True).method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key="health.heartbeat")

    print(" [*] Aguardando batimentos cardíacos...")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    consume_heartbeat()
