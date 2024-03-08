from pytest import mark

# APy
from api import hello, health


class TestRoot:
    @mark.asyncio
    async def test_health(self) -> None:
        # Arrange
        expected: dict = {"message": "The state of the service is healthy."}

        # Act
        actual: dict = await health()

        # Assert
        assert expected == actual

    @mark.asyncio
    async def test_hello(self) -> None:
        # Arrange
        expected: dict = {"message": "Hello World !"}

        # Act
        actual: dict = await hello()

        # Assert
        assert expected == actual
