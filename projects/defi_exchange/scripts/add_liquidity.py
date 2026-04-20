import logging
import algokit_utils
from smart_contracts.artifacts.amm_pool.amm_pool_client import AmmPoolClient
from algosdk import transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_liquidity(app_id: int, token_a_id: int, token_b_id: int, amount_a: int, amount_b: int):
    algorand = algokit_utils.AlgorandClient.default_local_net()
    deployer = algorand.account.from_environment("DEPLOYER")
    
    app_client = AmmPoolClient(
        algod_client=algorand.client.algod,
        app_id=app_id,
        signer=deployer.signer,
    )
    
    logger.info(f"Adding liquidity to Pool {app_id}: {amount_a} of {token_a_id} and {amount_b} of {token_b_id}")
    
    # 1. Asset Transfers to the App
    sp = algorand.client.algod.suggested_params()
    axfer_a = transaction.AssetTransferTxn(
        sender=deployer.address,
        sp=sp,
        receiver=app_client.app_address,
        amt=amount_a,
        index=token_a_id
    )
    
    axfer_b = transaction.AssetTransferTxn(
        sender=deployer.address,
        sp=sp,
        receiver=app_client.app_address,
        amt=amount_b,
        index=token_b_id
    )
    
    # 2. Call add_liquidity
    # Note: Typed clients handle atomic groups if configured, 
    # but here we pass the transactions as arguments to the ABI method.
    result = app_client.add_liquidity(
        axfer_a=axfer_a,
        axfer_b=axfer_b,
    )
    
    logger.info(f"Liquidity added! LP Tokens minted: {result.abi_return}")

if __name__ == "__main__":
    # Example usage (replace with actual IDs after deployment)
    # add_liquidity(APP_ID, TOKEN_A, TOKEN_B, 1000000, 1000000)
    print("Please run this script with correct APP_ID and TOKEN IDs.")
