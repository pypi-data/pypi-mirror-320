import logging
from typing import TYPE_CHECKING

import conf_rabbit
from conf_rabbit import configure_logging
from conf_rabbit import get_connection


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic
    from pika.spec import BasicProperties

logger = logging.getLogger(__name__)


def process_new_message(ch: 'BlockingChannel', method: 'Basic.Deliver', properties: 'BasicProperties', body: bytes):
    logger.info(f'{ch=}')
    logger.info(f'{method=}')
    logger.info(f'{properties=}')
    logger.info(f'{body=}')

    ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждение получения сообщения в ручном режиме
    logger.warning(f'Finish processing logging | {body}')


def consume_messages(channel: 'BlockingChannel'):
    """Получение"""
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=conf_rabbit.MQ_ROUTING_KEY,
        on_message_callback=process_new_message,
        # auto_ack=True # Автоматическое подтверждение о получение сообщении
    )
    logger.warning('Waiting for messages')
    channel.start_consuming()


def main():
    configure_logging(level=logging.WARNING)
    with get_connection() as connection:
        logger.info(f'Created connection:{connection}')

        with connection.channel() as channel:
            logger.info(f'Created channel: {channel}')
            consume_messages(channel=channel)

            while True:
                pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Received interrupt')
