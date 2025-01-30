from pytest import mark

from pycharting.api import calc


class TestCalc:
    @mark.asyncio
    async def test_calc_add(self):
        # Arrange
        operator: str = "+"
        terms: list[float] = [0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        expected: float = 45.1

        # Act
        actual: dict = await calc(operator, terms)

        # Assert
        assert expected == actual["result"]

    @mark.asyncio
    async def test_calc_substract(self):
        # Arrange
        operator: str = "-"
        terms: list[float] = [0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        expected: float = -45.1

        # Act
        actual: dict = await calc(operator, terms)

        # Assert
        assert expected == actual["result"]

    @mark.asyncio
    async def test_calc_multiply(self):
        # Arrange
        operator: str = "*"
        terms: list[float] = [0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        expected: float = 36288.00000000001

        # Act
        actual: dict = await calc(operator, terms)

        # Assert
        assert expected == actual["result"]

    @mark.asyncio
    async def test_calc_divide(self):
        # Arrange
        operator: str = "÷"
        terms: list[float] = [0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        expected: float = 2.7557319223985896e-05

        # Act
        actual: dict = await calc(operator, terms)

        # Assert
        assert expected == actual["result"]
