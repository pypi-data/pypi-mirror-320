import logging

from .rabbitmq.rabbitmq_consumer import RabbitMQConsumerBase
from .rabbitmq.rabbitmq_utils import (
    validate_log_collector_msg_body,
    decode_body_bytes,
    publish_message_to_rabbitmq,
)
from ..log_service.logcollector_controller import LogCollectorController
from pika import spec

logger = logging.getLogger("rabbitmq")


class CoreConsumer(RabbitMQConsumerBase):
    def __init__(self, binding_info, host, port, username, password):
        super().__init__(binding_info, host, port, username, password)
        self.controller = LogCollectorController()

    def process_message(
        self,
        channel,
        method: spec.Basic.Deliver,
        properties: spec.BasicProperties,
        body: bytes,
    ):
        logger.info(
            f"ch:{channel}, method:{method}, properties:{properties}, body:{body}"
        )

        (msg, service, data, action) = validate_log_collector_msg_body(
            decode_body_bytes(body)
        )

        action_mapper = {
            "connect": self.controller.connect,
            "disconnect": self.controller.disconnect,
            "reconnect": self.controller.reconnect,
            "close": self.controller.close,
            "dummy": self.controller.dummy,
            "command": self.controller.command,
            "setup_response": self.controller.setup_response,
        }

        # connect, disconnect, reconnect
        if action:
            response = action_mapper[action](data)
        else:
            response = action_mapper[msg](data)
        logger.info(f"response: {msg}({data}) => {response}")

        # 모든 요청은 응답을 보내도록 되어 있음
        if response is not None:
            publish_message_to_rabbitmq(
                exchange=response["exchange"],
                routing_key=response["routing_key"],
                body=response["message"],
            )
