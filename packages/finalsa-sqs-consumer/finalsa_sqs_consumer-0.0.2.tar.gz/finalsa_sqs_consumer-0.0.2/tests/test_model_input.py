from finalsa.sqs.consumer import (
    SqsApp, SqsAppTest)
from uuid import UUID
from pydantic import BaseModel


def test_get_correlation_id():
    app = SqsApp()

    @app.handler("test")
    async def handler(correlation_id: str):
        assert correlation_id == "test-test"

    app_test = SqsAppTest(app)
    app_test.consume("test", {})


def test_get_id():
    app = SqsApp()

    @app.handler("test")
    async def handler(id: UUID):
        assert isinstance(id, UUID)

    app_test = SqsAppTest(app)
    app_test.consume("test", {})


def test_parse_body():
    app = SqsApp()

    class Request(BaseModel):
        id: UUID

    @app.handler("test")
    async def handler(request: Request):
        assert isinstance(request.id, UUID)

    app_test = SqsAppTest(app)
    app_test.consume("test", {
        "id": "f4b2e7f6-7a0d-4b9e-8e2d-4d0e0d4b3f5d"
    })


def test_parse_body_and_correlation_id():
    app = SqsApp()

    class Request(BaseModel):
        id: UUID

    @app.handler("test")
    async def handler(request: Request, correlation_id: str):
        assert isinstance(request.id, UUID)
        assert correlation_id == "test-test"

    app_test = SqsAppTest(app)
    app_test.consume("test", {
        "id": "f4b2e7f6-7a0d-4b9e-8e2d-4d0e0d4b3f5d"
    })
