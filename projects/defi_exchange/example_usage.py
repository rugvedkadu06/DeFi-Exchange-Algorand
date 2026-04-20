import logging
import algokit_utils
from algokit_utils.beta.algorand_client import AlgorandClient
from smart_contracts.artifacts.defi_exchange.defi_exchange_client import DefiExchangeFactory
from smart_contracts.artifacts.amm_pool.amm_pool_client import AmmPoolFactory
from smart_contracts.artifacts.swap.swap_client import SwapFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_example():
    # Initialize Algorand client
    algorand = AlgorandClient.default_local_net()
    deployer = algorand.account.from_environment("DEPLOYER")

    # 1. Deploy DeFi Exchange
    exchange_factory = algorand.client.get_typed_app_factory(
        DefiExchangeFactory, default_sender=deployer.address
    )
    exchange_client, _ = exchange_factory.deploy()
    logger.info(f"DeFi Exchange deployed at: {exchange_client.app_id}")

    # 2. Register a Pool
    # For demonstration, we'll use placeholder asset IDs (e.g., 1001, 1002)
    # In a real scenario, you would create these assets first.
    pool_id = exchange_client.send.register_pool(
        args={"token_a": 1001, "token_b": 1002}
    ).abi_return
    logger.info(f"Registered Pool ID: {pool_id}")

    # 3. Deploy an AMM Pool Instance
    amm_factory = algorand.client.get_typed_app_factory(
        AmmPoolFactory, default_sender=deployer.address
    )
    amm_client, _ = amm_factory.deploy()
    logger.info(f"AMM Pool Instance deployed at: {amm_client.app_id}")

    # 4. Initialize Pool
    # amm_client.send.create_pool(args={"token_a": 1001, "token_b": 1002})
    # Note: This requires the contract to have ALGOs and the assets to exist.

    logger.info("Example setup complete. Contracts are ready for interaction.")

if __name__ == "__main__":
    run_example()
