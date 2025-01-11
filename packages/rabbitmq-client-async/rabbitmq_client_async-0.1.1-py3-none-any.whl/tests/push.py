import asyncio
import logging
from random import randint

from config_logs import configure_logging
from rabbitmq_async_client.rabbitmq_client import RabbitMQClient


logger = logging.getLogger(__name__)


async def main():
    configure_logging(level=logging.INFO)

    client = RabbitMQClient(host='localhost', port=5672, user='guest', password='guest', durable=True)

    try:
        # for i in range(1, 11):
        stop = randint(1, 100)
        while stop != 55:
            queue, key, value = randint(1, 2), randint(1, 10), randint(1, 10)
            data = {f'example_key_{key:<2}': f'example_value_{value:<2}'}
            await client.publisher(f'queue_{queue}', data)
            stop = randint(1, 100)

    except KeyboardInterrupt:
        await client.stop()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Publisher interrupt')
