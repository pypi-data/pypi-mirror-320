import asyncio
import logging
import os
import sys


DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(DIR_PATH)

from rabbitmq_async_client.rabbitmq_client import RabbitMQClient  # noqa: E402


logger = logging.getLogger(__name__)


async def process_queue_1(message):
    logger.info(f'Обработка сообщения из queue_1: {message}')


async def process_queue_2(message):
    logger.info(f'Обработка сообщения из queue_2: {message}')


async def main():
    client = RabbitMQClient(host='localhost', port=5672, user='guest', password='guest', durable=True)

    callbacks = {
        'queue_1': process_queue_1,
        'queue_2': process_queue_2,
    }

    try:
        await client.consumer(process_message_callbacks=callbacks)
    except KeyboardInterrupt:
        await client.stop()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Consumer interrupt')
