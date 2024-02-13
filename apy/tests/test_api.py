from apy.main import hello, root
from pytest import mark


@mark.asyncio
async def test_root() -> None:
    # Arrange
    expected: dict = {"message": "The state of the service is healthy."}

    # Act
    actual: dict = await root()

    # Assert
    assert expected == actual


@mark.asyncio
async def test_hello() -> None:
    # Arrange
    expected: dict = {"message": "Hello World !"}

    # Act
    actual: dict = await hello()

    # Assert
    assert expected == actual
