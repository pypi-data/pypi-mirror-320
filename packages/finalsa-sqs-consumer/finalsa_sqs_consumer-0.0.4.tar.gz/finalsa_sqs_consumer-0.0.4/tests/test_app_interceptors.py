from finalsa.sqs.consumer import (
    SqsApp, SqsAppTest, AsyncConsumerInterceptor)
from finalsa.common.models import SqsMessage
from typing import Callable


def test_error_interceptor():
    class TestInterceptor(AsyncConsumerInterceptor):
        async def __call__(self, message: SqsMessage, call_next: Callable):
            try:
                message.correlation_id = "dasdasdnkajsndkjasn"
                await call_next(message)
            except Exception as ex:
                print(ex)

    app = SqsApp(
        interceptors=[TestInterceptor]
    )

    @app.handler("test")
    async def handler(correlation_id: str):
        print("test")
        raise Exception("pu")

    app_test = SqsAppTest(app)
    app_test.consume("test", {})


def test_error_interceptor():
    class CorrelationInterceptorOne(AsyncConsumerInterceptor):
        async def __call__(self, message: SqsMessage, call_next: Callable):
            try:
                message.correlation_id = "dasdasdnkajsndkjasn"
                await call_next(message)
            except Exception as ex:
                print(ex)

    class CorrelationInterceptorTwo(AsyncConsumerInterceptor):
        async def __call__(self, message: SqsMessage, call_next: Callable):
            try:
                message.correlation_id = "dasdasdnkajsndkjasna"
                await call_next(message)
            except Exception as ex:
                print(ex)

    app = SqsApp(
        interceptors=[CorrelationInterceptorOne, CorrelationInterceptorTwo]
    )

    @app.handler("test")
    async def handler(correlation_id: str):
        assert correlation_id == "dasdasdnkajsndkjasna"
        raise Exception("pu")

    app_test = SqsAppTest(app)
    app_test.consume("test", {})
