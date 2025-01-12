from finalsa.sqs.consumer import (
    SqsApp, SqsAppTest, TopicNotFoundException)


def test_app_test_topic():
    app = SqsApp()
    db = 0

    @app.handler("test")
    async def handler():
        nonlocal db
        db = 1
    app_test = SqsAppTest(app)
    app_test.consume("test", {})
    assert db == 1


def test_app_incorrect_topic():
    app = SqsApp()

    @app.handler("test")
    async def handler():
        print("test")
    app_test = SqsAppTest(app)
    try:
        app_test.consume("test2", {})
    except TopicNotFoundException as ex:
        assert str(ex) == str(TopicNotFoundException("test2"))
