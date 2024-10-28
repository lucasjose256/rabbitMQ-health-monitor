import pika
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

EXCHANGE_NAME = 'sensor_exchange'

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

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

channel.queue_declare(queue='heartbeat_queue')
channel.queue_bind(exchange=EXCHANGE_NAME, queue='heartbeat_queue', routing_key="health.heartbeat")

def callback(ch, method, properties, body):
    payload = json.loads(body)
    message = payload['message']
    signature = payload['signature']
    public_key_pem = payload['public_key']

    if verify_signature(message, signature, public_key_pem):
        data = json.loads(message)
        heartbeat = data['heartbeat']
        print(f"Assinatura verificada! Batimento cardíaco recebido: {heartbeat}")

        # Monitorar valor de batimento cardíaco (ajuste os valores de alerta conforme necessário)
        if heartbeat < 60 or heartbeat > 100:
            print(" [!] Alerta: Batimento cardíaco fora do intervalo normal!")
        else:
            print(" [OK] Batimento cardíaco dentro do intervalo normal.")
    else:
        print("Assinatura inválida. Mensagem não confiável.")

channel.basic_consume(
    queue='heartbeat_queue',
    on_message_callback=callback,
    auto_ack=True
)

print("Aguardando mensagens...")
channel.start_consuming()
