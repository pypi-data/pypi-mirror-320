import asyncio
import logging

from config_logs import configure_logging
from rabbitmq_async_client.rabbitmq_client import RabbitMQClient


logger = logging.getLogger(__name__)

RABBITMQ_SETTINGS = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'password': 'guest',
    'durable': True,  # Делает очереди устойчивыми
}


async def initialize_queues():
    """Инициализация очередей с использованием RabbitMQClient"""
    client = RabbitMQClient(
        host=RABBITMQ_SETTINGS['host'],
        port=RABBITMQ_SETTINGS['port'],
        user=RABBITMQ_SETTINGS['user'],
        password=RABBITMQ_SETTINGS['password'],
        durable=RABBITMQ_SETTINGS['durable'],
    )
    await client.declare_queues()


async def main():
    configure_logging(level=logging.INFO)
    await initialize_queues()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Process interrupted')
