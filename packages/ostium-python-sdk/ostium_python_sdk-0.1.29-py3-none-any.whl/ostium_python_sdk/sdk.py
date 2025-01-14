from dotenv import load_dotenv
import os

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
