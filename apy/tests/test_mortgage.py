from pytest import mark

# APy
from api import mortgage


class TestMortgage:
    @mark.asyncio
    async def test_mortgage_median(self):
        # Arrange
        request: dict = {
            "loan": 506500.00,
            "rate": 0.0534,
            "duration": 25
        }
        expected: dict = {
            "request": {
                "loan": 506500.0,
                "rate": 0.0534,
                "duration": 25
            },
            "response": {
                "monthly": {
                    "capital": 1688.46,
                    "interest": 1373.68,
                    "payment": 3062.14
                },
                "total": {
                    "interest": 412142.0,
                    "payment": 918642.0
                },
                "rate": {
                    "interest": 0.4486,
                    "payment": 1.81
                }
            }
        }

        # Act
        actual: dict = await mortgage(request)

        # Assert
        assert expected == actual

    @mark.asyncio
    async def test_mortgage_2539_rue_l_o_david_montreal(self):
        # Arrange
        request: dict = {
            "loan": 1786000.00,
            "rate": 0.0534,
            "duration": 25
        }
        expected: dict = {
            "request": {
                "loan": 1786000.0,
                "rate": 0.0534,
                "duration": 25
            },
            "response": {
                "monthly": {
                    "capital": 5953.8,
                    "interest": 4843.81,
                    "payment": 10797.61
                },
                "total": {
                    "interest": 1453283.0,
                    "payment": 3239283.0
                },
                "rate": {
                    "interest": 0.4486,
                    "payment": 1.81
                }
            }
        }

        # Act
        actual: dict = await mortgage(request)

        # Assert
        assert expected == actual
