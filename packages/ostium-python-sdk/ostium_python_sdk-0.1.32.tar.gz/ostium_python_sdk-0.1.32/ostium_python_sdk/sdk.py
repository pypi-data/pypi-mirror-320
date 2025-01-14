from dotenv import load_dotenv
import os
from decimal import Decimal
from .constants import PRECISION_2, PRECISION_6, PRECISION_12, PRECISION_18, PRECISION_9

from ostium_python_sdk.faucet import Faucet
from .balance import Balance
from .price import Price
from web3 import Web3
from .ostium import Ostium
from .config import NetworkConfig
from typing import Union
from .subgraph import SubgraphClient


class OstiumSDK:
    def __init__(self, network: Union[str, NetworkConfig], private_key: str = None, rpc_url: str = None):
        load_dotenv()
        self.private_key = private_key or os.getenv('PRIVATE_KEY')
        if not self.private_key:
            raise ValueError(
                "No private key provided. Please provide via constructor or PRIVATE_KEY environment variable")

        self.rpc_url = rpc_url or os.getenv('RPC_URL')
        if not self.rpc_url:
            network_name = "mainnet" if isinstance(
                network, str) and network == "mainnet" else "testnet"
            raise ValueError(
                f"No RPC URL provided for {network_name}. Please provide via constructor or RPC_URL environment variable")

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Get network configuration
        if isinstance(network, NetworkConfig):
            self.network_config = network
        elif isinstance(network, str):
            if network == "mainnet":
                self.network_config = NetworkConfig.mainnet()
            elif network == "testnet":
                self.network_config = NetworkConfig.testnet()
            else:
                raise ValueError(
                    f"Unsupported network: {network}. Use 'mainnet' or 'testnet'")
        else:
            raise ValueError(
                "Network must be either a NetworkConfig instance or a string ('mainnet' or 'testnet')")

        # Initialize Ostium instance
        self.ostium = Ostium(
            self.w3,
            self.network_config.contracts["usdc"],
            self.network_config.contracts["tradingStorage"],
            self.network_config.contracts["trading"],
            private_key=self.private_key
        )

        # Initialize subgraph client
        self.subgraph = SubgraphClient(url=self.network_config.graph_url)

        self.balance = Balance(self.w3, self.network_config.contracts["usdc"])
        self.price = Price()

        if self.network_config.is_testnet:
            self.faucet = Faucet(self.w3, self.private_key)
        else:
            self.faucet = None

    async def get_formatted_pairs_details(self) -> list:
        """
        Get formatted details for all trading pairs, with proper decimal conversion.

        Crypto pairs example:
        BTC-USD:
            - price: 65432.50
            - longOI: 0.41008148 (410.08148 BTC)
            - shortOI: 2.59812309 (2,598.12309 BTC)
            - maxOI: 1000.00000000
            - utilizationP: 80.00%
            - makerFeeP: 0.01%
            - takerFeeP: 0.10%
            - maxLeverage: 50x
            - group: crypto

        ETH-USD:
            - price: 3050.50
            - longOI: 5.90560023 (5,905.60023 ETH)
            - shortOI: 0.00000000
            - maxOI: 1000.00000000
            - utilizationP: 80.00%
            - makerFeeP: 0.01%
            - takerFeeP: 0.10%
            - maxLeverage: 50x
            - group: crypto

        Returns:
            list: List of dictionaries containing formatted pair details including:
                - id: Pair ID
                - from: Base asset (e.g., 'BTC')
                - to: Quote asset (e.g., 'USD')
                - price: Current market price
                - isMarketOpen: Market open status
                - longOI: Total long open interest in notional value
                - shortOI: Total short open interest in notional value
                - maxOI: Maximum allowed open interest
                - utilizationP: Utilization threshold percentage
                - makerFeeP: Maker fee percentage
                - takerFeeP: Taker fee percentage
                - usageFeeP: Usage fee percentage
                - maxLeverage: Maximum allowed leverage
                - minLeverage: Minimum allowed leverage
                - makerMaxLeverage: Maximum leverage for makers
                - group: Trading group name
                - groupMaxCollateralP: Maximum collateral percentage for the group
                - minLevPos: Minimum leverage position size
                - lastFundingRate: Latest funding rate
                - curFundingLong: Current funding for longs
                - curFundingShort: Current funding for shorts
                - lastFundingBlock: Block number of last funding update
                - lastFundingVelocity: Velocity of last funding rate change
        """
        pairs = await self.subgraph.get_pairs()
        formatted_pairs = []

        for pair in pairs:
            pair_details = await self.subgraph.get_pair_details(pair['id'])

            # Get current price and market status
            try:
                price, is_market_open = await self.price.get_price(
                    pair_details['from'],
                    pair_details['to']
                )
            except ValueError:
                price = 0
                is_market_open = False

            formatted_pair = {
                'id': int(pair_details['id']),
                'from': pair_details['from'],
                'to': pair_details['to'],
                'price': price,
                'isMarketOpen': is_market_open,
                'longOI': Decimal(pair_details['longOI']) / PRECISION_18,
                'shortOI': Decimal(pair_details['shortOI']) / PRECISION_18,
                'maxOI': Decimal(pair_details['maxOI']) / PRECISION_6,
                'utilizationP': Decimal(pair_details['utilizationThresholdP']) / PRECISION_2,
                'makerFeeP': Decimal(pair_details['makerFeeP']) / PRECISION_6,
                'takerFeeP': Decimal(pair_details['takerFeeP']) / PRECISION_6,
                'usageFeeP': Decimal(pair_details['usageFeeP']) / PRECISION_6,
                'maxLeverage': Decimal(pair_details['group']['maxLeverage']) / PRECISION_2,
                'minLeverage': Decimal(pair_details['group']['minLeverage']) / PRECISION_2,
                'makerMaxLeverage': Decimal(pair_details['makerMaxLeverage']) / PRECISION_2,
                'group': pair_details['group']['name'],
                'groupMaxCollateralP': Decimal(pair_details['group']['maxCollateralP']) / PRECISION_2,
                'minLevPos': Decimal(pair_details['fee']['minLevPos']) / PRECISION_9,
                'lastFundingRate': Decimal(pair_details['lastFundingRate']) / PRECISION_9,
                'curFundingLong': Decimal(pair_details['curFundingLong']) / PRECISION_9,
                'curFundingShort': Decimal(pair_details['curFundingShort']) / PRECISION_9,
                'lastFundingBlock': int(pair_details['lastFundingBlock']),
                'lastFundingVelocity': int(pair_details['lastFundingVelocity'])
            }
            formatted_pairs.append(formatted_pair)

        return formatted_pairs
