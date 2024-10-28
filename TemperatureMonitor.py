import pika
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

EXCHANGE_NAME = 'health_exchange'

def verify_signature(message, signature, public_key_pem):
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    try:
        public_key.verify(
            bytes.fromhex(signature),
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print("Erro de verificação:", e)
        return False

def callback(ch, method, properties, body):
    payload = json.loads(body)
    message = payload['message']
    signature = payload['signature']
    public_key_pem = payload['public_key']

    if verify_signature(message, signature, public_key_pem):
        data = json.loads(message)
        temperature = data['temperature']
        print(f"Assinatura verificada! Temperatura corporal recebida: {temperature}")

        if temperature < 36.0 or temperature > 37.5:
            print(" [!] Atenção: Temperatura fora do normal:", temperature)
        else:
            print(" [OK] Temperatura dentro do intervalo normal.")
    else:
        print("Assinatura inválida. Mensagem não confiável.")

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
