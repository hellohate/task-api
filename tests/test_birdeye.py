import unittest
from unittest.mock import patch, Mock
from decimal import Decimal
from birdeye import BirdEyeClient, NoPositionsError
from clients.common import PriceInfo, TokenOverview
from custom_exceptions import InvalidSolanaAddress, InvalidTokens


class TestBirdEyeClient(unittest.TestCase):

    @patch('BirdEyeClient.requests.get')
    def test_fetch_prices(self, mock_get):
        client = BirdEyeClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC": {
                "price": "1.0",
                "liquidity": "100.0"
            },
            "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj": {
                "price": "2.0",
                "liquidity": "200.0"
            }
        }
        mock_get.return_value = mock_response

        token_addresses = [
            "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC",
            "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj"
        ]
        expected_output = {
            "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC": PriceInfo(price=Decimal("1.0"), liquidity=Decimal("100.0")),
            "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj": PriceInfo(price=Decimal("2.0"), liquidity=Decimal("200.0"))
        }
        self.assertEqual(client.fetch_prices(token_addresses), expected_output)

    @patch('BirdEyeClient.requests.get')
    def test_fetch_prices_no_tokens(self, mock_get):
        client = BirdEyeClient()
        with self.assertRaises(NoPositionsError):
            client.fetch_prices([])

    @patch('BirdEyeClient.requests.get')
    def test_fetch_token_overview(self, mock_get):
        client = BirdEyeClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "SOL",
            "name": "Solana",
            "price": "50.0",
            "market_cap": "100000000.0",
            "volume_24h": "5000000.0",
            "circulating_supply": "2000000.0",
            "total_supply": "3000000.0"
        }
        mock_get.return_value = mock_response

        address = "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC"
        expected_output = TokenOverview(
            symbol="SOL",
            name="Solana",
            price=Decimal("50.0"),
            market_cap=Decimal("100000000.0"),
            volume_24h=Decimal("5000000.0"),
            circulating_supply=Decimal("2000000.0"),
            total_supply=Decimal("3000000.0")
        )
        self.assertEqual(client.fetch_token_overview(address), expected_output)

    @patch('BirdEyeClient.requests.get')
    def test_fetch_token_overview_invalid_address(self, mock_get):
        client = BirdEyeClient()
        invalid_address = "InvalidAddress"
        with self.assertRaises(InvalidSolanaAddress):
            client.fetch_token_overview(invalid_address)

if __name__ == '__main__':
    unittest.main()
