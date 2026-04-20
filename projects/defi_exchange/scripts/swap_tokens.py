import logging
import algokit_utils
from smart_contracts.artifacts.swap.swap_client import SwapClient
from algosdk import transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def perform_swap(app_id: int, token_in_id: int, amount_in: int, is_a_to_b: bool):
    algorand = algokit_utils.AlgorandClient.default_local_net()
    deployer = algorand.account.from_environment("DEPLOYER")
    
    app_client = SwapClient(
        algod_client=algorand.client.algod,
        app_id=app_id,
        signer=deployer.signer,
    )
    
    logger.info(f"Swapping {amount_in} of token {token_in_id} via Swap app {app_id}")
    
    sp = algorand.client.algod.suggested_params()
    axfer = transaction.AssetTransferTxn(
        sender=deployer.address,
        sp=sp,
        receiver=app_client.app_address,
        amt=amount_in,
        index=token_in_id
    )
    
    if is_a_to_b:
        result = app_client.swap_a_to_b(axfer=axfer)
    else:
        result = app_client.swap_b_to_a(axfer=axfer)
        
    logger.info(f"Swap executed! Amount out: {result.abi_return}")

if __name__ == "__main__":
    # Example usage:
    # perform_swap(APP_ID, TOKEN_ID, 10000, True)
    print("Please run this script with correct APP_ID and TOKEN IDs.")
