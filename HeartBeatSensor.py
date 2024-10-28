import pika
import json
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization

EXCHANGE_NAME = 'sensor_exchange'

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()


def sign_message(message):
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

while True:
    heartbeat = int(input("Digite o valor do batimento cardíaco: "))
    message = json.dumps({"device_id": 1, "heartbeat": heartbeat, "timestamp": time.time()})

    signature = sign_message(message).hex()
    signed_message = json.dumps({
        "message": message,
        "signature": signature,
        "public_key": public_pem
    })

    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="health.heartbeat", body=signed_message)
    print(" [x] Enviou batimentos cardíacos:", signed_message)
    time.sleep(5)
