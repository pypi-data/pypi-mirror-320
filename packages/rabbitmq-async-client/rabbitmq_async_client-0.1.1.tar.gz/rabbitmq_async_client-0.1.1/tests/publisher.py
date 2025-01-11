import logging
from random import randint
from typing import TYPE_CHECKING

import conf_rabbit
from conf_rabbit import configure_logging
from conf_rabbit import get_connection


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

logger = logging.getLogger(__name__)


def produce_message(channel: 'BlockingChannel'):
    """отправка"""
    queue = channel.queue_declare(queue=conf_rabbit.MQ_ROUTING_KEY)  # Создание очереди если еще не создана
    logger.info(f"Declared queue: '{conf_rabbit.MQ_ROUTING_KEY}' | {queue}")

    message_body = f'Hello World! {randint(1, 100)}'
    logger.debug('Sending message: %s', message_body)
    channel.basic_publish(
        exchange=conf_rabbit.MQ_EXCHANGE,  # direct
        routing_key=conf_rabbit.MQ_ROUTING_KEY,
        body=message_body,
    )
    logger.warning('Published sent')


def main():
    configure_logging(level=logging.DEBUG)
    with get_connection() as connection:
        logger.info(f'Created connection:{connection}')

        with connection.channel() as channel:
            logger.info(f'Created channel: {channel}')
            produce_message(channel=channel)

            while True:
                pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Received interrupt')
