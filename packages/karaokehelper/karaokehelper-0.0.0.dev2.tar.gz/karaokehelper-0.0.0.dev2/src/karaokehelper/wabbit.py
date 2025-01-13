import pika
from time import sleep


class WabbitMQ:
    def __init__(self, queue_name: str, server: str = 'localhost'):
        self.server = server
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.server, heartbeat=300))
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.queue = self.create_queue()

    def create_queue(self):
        return self.channel.queue_declare(queue=self.queue_name)

    def publish(self, message: str):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)
        print(f" [x] Sent:    {message}")

    def consume(self, callback: object = None):
        def _callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f" [x] Received: {message}")
            sleep(1)

        callback = callback if callback is not None else _callback
        self.channel.basic_consume(queue=self.queue_name, auto_ack=True, on_message_callback=callback)
        while True:
            try:
                print(' [*] Waiting for messages. To exit press CTRL+C')
                self.channel.start_consuming()
            except ConnectionResetError:
                pass

    def __del__(self):
        self.connection.close()