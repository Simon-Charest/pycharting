from pytest import mark

from pycharting.api import health, root


class TestRoot:
    @mark.asyncio
    async def test_root_serves_the_collection_page(self) -> None:
        # Act
        actual = await root()

        # Assert
        assert 200 == actual.status_code
        assert str(actual.path).endswith("collection.html")
        assert "no-cache" == actual.headers["cache-control"]

    @mark.asyncio
    async def test_health(self) -> None:
        # Arrange
        expected: dict = {"message": "The state of the service is healthy."}

        # Act
        actual: dict = await health()

        # Assert
        assert expected == actual
