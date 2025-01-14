import aiohttp
import json
from typing import Tuple


class Price:
    def __init__(self):
        self.base_url = "https://listener.ostium.io"

    async def get_latest_prices(self):
        """
        Fetches the latest prices from the Ostium price listener service.
        Returns a dictionary of price data.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/PricePublish/latest-prices") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(
                        f"Failed to fetch prices: {response.status}")

    async def get_price(self, from_asset: str, to_asset: str) -> Tuple[float, bool]:
        """
        Get the latest price and market status for a specific asset pair.
        Args:
            from_asset: The base asset symbol (e.g., "BTC")
            to_asset: The quote asset symbol (e.g., "USD")
        Returns:
            Tuple[float, bool]: The latest price and market open status for the asset pair
        """
        prices = await self.get_latest_prices()
        for price_data in prices:
            if (price_data.get('from') == from_asset and
                    price_data.get('to') == to_asset):
                return float(price_data.get('mid', 0)), price_data.get('isMarketOpen', False)
        raise ValueError(f"No price found for pair: {from_asset}/{to_asset}")
