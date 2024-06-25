import requests
from decimal import Decimal
from typing import List, Dict
from custom_exceptions import *
from clients.common import PriceInfo, TokenOverview
from utils.helpers import is_solana_address


class Config:
    BIRD_EYE_TOKEN = "451846c7a9bc440d933652aba468b9e9"


class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": Config.BIRD_EYE_TOKEN,
        }

    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        match method.upper():
            case "GET":
                query_method = requests.get
            case "POST":
                query_method = requests.post
            case _:
                raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)
        return resp

    def fetch_prices(self, token_addresses: List[str]) -> Dict[str, PriceInfo]:
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
            dict[str, PriceInfo]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """
        if not token_addresses:
            raise NoPositionsError("No token addresses provided")

        url = "https://public-api.birdeye.so/public/price"
        params = {
            "tokens": ",".join(token_addresses)
        }

        response = self._make_api_call("GET", url, params=params)
        if response.status_code != 200:
            raise InvalidTokens()

        data = response.json()
        prices = {}
        for token in token_addresses:
            token_data = data.get(token)
            if token_data:
                price = Decimal(token_data['price'])
                liquidity = Decimal(token_data['liquidity'])
                prices[token] = PriceInfo(value=price, liquidity=liquidity)
            else:
                prices[token] = PriceInfo(value=Decimal(0), liquidity=Decimal(0))
        return prices

    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            TokenOverview: Overview with token information

        Raises:
            InvalidSolanaAddress: Raised if invalid solana address is passed
            InvalidTokens: Raised if the API call was unsuccessful
        """
        if not is_solana_address(address):
            raise InvalidSolanaAddress(f"Invalid Solana address: {address}")

        url = f"https://public-api.birdeye.so/public/token/{address}"

        response = self._make_api_call("GET", url)
        if response.status_code != 200:
            raise InvalidTokens()

        data = response.json()

        # Create and return a TokenOverview namedtuple instance
        return TokenOverview(
            price=Decimal(data['price']),
            symbol=data['symbol'],
            decimals=data.get('decimals', None),  # Assuming 'decimals' might be optional or handled differently
            lastTradeUnixTime=data.get('lastTradeUnixTime', None),
            liquidity=data.get('liquidity', None),
            supply=data.get('supply', None)
        )
