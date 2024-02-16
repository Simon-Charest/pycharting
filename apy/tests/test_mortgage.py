from apy.main import mortgage
from pytest import mark


class TestMortgage:
    @mark.asyncio
    async def test_mortgage_add(self):
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
