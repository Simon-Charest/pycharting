from apy.main import select
from pytest import mark


class TestDb:
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
        assert 0 == len(actual)
