import asyncio
import json
import logging
import os
import sys
from typing import Callable
from typing import TYPE_CHECKING

import aio_pika
from aio_pika import connect_robust

from config_logs import configure_logging


if TYPE_CHECKING:
    from aio_pika.abc import AbstractChannel
    from aio_pika.abc import AbstractRobustConnection

logger = logging.getLogger(__name__)


QUEUES = ['queue_1', 'queue_2']


class RabbitMQClient:
    """
    Універсальний клієнт для роботи з RabbitMQ, що підтримує відправку та отримання повідомлень.
    Тепер підтримує асинхронний режим.
    """

    def __init__(self, host: str, port: int, user: str, password: str, durable: bool = False):
        """
        Ініціалізує клієнта RabbitMQ з параметрами з'єднання та задає черги для відправки/отримання повідомлень.
        Асинхронний варіант.
        """
        self.queues = QUEUES
        self.durable = durable
        self.host, self.port, self.user, self.password = host, port, user, password

        # Конфігурація логування
        configure_logging(level=logging.INFO)

        # Створення з'єднання та каналу з RabbitMQ
        self.connection = None
        self.channel = None

    async def get_connection(self) -> 'AbstractRobustConnection':
        """
        Встановлює та повертає асинхронне з'єднання з RabbitMQ.
        """
        if not self.connection:
            self.connection = await connect_robust(f'amqp://{self.user}:{self.password}@{self.host}:{self.port}/')
        return self.connection

    async def get_channel(self) -> 'AbstractChannel':
        """
        Створює та повертає асинхронний канал для роботи з RabbitMQ.
        """
        if not self.channel:
            self.connection = await self.get_connection()
            self.channel = await self.connection.channel()
        return self.channel

    async def declare_queues(self):
        """
        Оголошує черги в RabbitMQ асинхронно.
        """
        self.channel = await self.get_channel()

        for queue in self.queues:
            await self.channel.declare_queue(queue, durable=self.durable)
            logger.info(f"Оголошено чергу: '{queue}'")

    async def publisher(self, queue_name: str, message: dict):
        """
        Асинхронно відправляє повідомлення в зазначену чергу RabbitMQ.
        """
        data_body = json.dumps(message)
        try:
            self.channel = await self.get_channel()

            await self.channel.default_exchange.publish(
                aio_pika.Message(body=data_body.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue_name,
            )
            logger.info(f"Повідомлення відправлено в чергу '{queue_name}': {message}")
        except Exception as e:
            logger.error(f'Помилка відправки повідомлення: {e}')
            raise

    async def consumer(self, process_message_callbacks: dict[str, Callable[[dict], None]]):
        """
        Асинхронно запускає процес споживання повідомлень з черг RabbitMQ.
        """
        logger.info('Розпочато отримання повідомлень з черг RabbitMQ.')
        self.channel = await self.get_channel()

        async def callback(queue_name: str):
            """
            Повертає асинхронну callback-функцію для обробки повідомлень з черги.
            """

            async def inner_callback(message: aio_pika.IncomingMessage):
                try:
                    async with message.process():
                        message_data = json.loads(message.body)
                        logger.info(f"Отримано повідомлення з черги '{queue_name}': {message_data}")
                        await process_message_callbacks[queue_name](message_data)
                except Exception as e:
                    logger.error(f"Помилка обробки повідомлення з черги '{queue_name}': {e}")

            return inner_callback

        for queue in self.queues:
            if queue in process_message_callbacks:
                await self.channel.set_qos(prefetch_count=1)
                queue_obj = await self.channel.declare_queue(queue, durable=self.durable)
                await queue_obj.consume(await callback(queue))

        try:
            await asyncio.Future()  # Ожидаем бесконечно
        except KeyboardInterrupt:
            pass

    async def stop(self):
        """
        Закриває асинхронно з'єднання з RabbitMQ.
        """
        if self.connection:
            await self.connection.close()
            logger.info("З'єднання з RabbitMQ закрите.")
