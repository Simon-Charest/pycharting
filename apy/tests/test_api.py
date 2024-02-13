from apy.main import hello, root, select
from pytest import mark


class TestMain:
    @mark.asyncio
    async def test_root(self) -> None:
        # Arrange
        expected: dict = {"message": "The state of the service is healthy."}

        # Act
        actual: dict = await root()

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

    @mark.asyncio
    async def test_select_all(self):
        # Arrange

        # Act
        actual: list = await select()

        # Assert
        assert isinstance(actual, list)

    @mark.asyncio
    async def test_select(self):
        # Arrange
        expected: str = "1"

        # Act
        actual = await select(expected)

        # Assert
        assert isinstance(actual, list)

    @mark.asyncio
    async def test_select_invalid_id(self):
        # Arrange
        expected: str = "0"

        # Act
        actual: dict = await select(expected)

        # Assert
        assert isinstance(actual, list)
        assert len(actual) == 0
