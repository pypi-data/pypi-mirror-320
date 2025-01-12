from finalsa.traceability.context import set_context_from_dict
from finalsa.sqs.client import SqsServiceTest
from finalsa.sns.client import SnsClientTest
from finalsa.common.models import SqsMessage
from finalsa.sqs.consumer.app import SqsApp
from uuid import uuid4
from asyncio import run
from typing import Any


class SqsAppTest():

    def __init__(self, app: SqsApp) -> None:
        self.app = app

    def consume(self, topic: str, payload: Any):
        self.app.__sqs__ = SqsServiceTest()
        self.app.__sns__ = SnsClientTest()
        correlation_id = f"test-{topic}"
        set_context_from_dict({"correlation_id": correlation_id}, self.app.app_name)
        message = SqsMessage(
            id=uuid4(),
            topic=topic,
            payload=payload,
            correlation_id=correlation_id
        )
        run(self.app.process_message(message))
