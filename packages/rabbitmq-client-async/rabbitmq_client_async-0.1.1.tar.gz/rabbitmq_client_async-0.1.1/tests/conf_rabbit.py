import logging

import pika

RABBIT_HOST = 'localhost'
RABBIT_PORT = 5672
RABBIT_USER = 'guest'
RABBIT_PASS = 'guest'
DURABLE = False

MQ_EXCHANGE = ''
MQ_ROUTING_KEY = 'news'


connection_params = pika.ConnectionParameters(
    host=RABBIT_HOST,
    port=RABBIT_PORT,
    credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASS),
)


def get_connection():
    return pika.BlockingConnection(parameters=connection_params)


def configure_logging(level: int = logging.DEBUG) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s",
    )
