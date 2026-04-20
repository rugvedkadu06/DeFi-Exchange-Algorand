import logging
import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk import transaction, account

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_asset(algod_client: AlgodClient, sender_address: str, private_key: str, asset_name: str, unit_name: str):
    params = algod_client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=sender_address,
        sp=params,
        total=1000000000000,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=sender_address,
        reserve=sender_address,
        freeze=sender_address,
        clawback=sender_address,
        decimals=6,
    )
    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    result = transaction.wait_for_confirmation(algod_client, txid, 4)
    asset_id = result["asset-index"]
    logger.info(f"Created {asset_name} ({unit_name}) with ID: {asset_id}")
    return asset_id

def main():
    # Connect to LocalNet
    algod_client = AlgodClient("a" * 64, "http://localhost:4001")
    
    # Get deployer account from environment (default LocalNet wallet)
    algorand = algokit_utils.AlgorandClient.default_localnet()
    deployer = algorand.account.from_environment("DEPLOYER")
    
    logger.info(f"Creating tokens using account: {deployer.address}")
    
    rug_id = create_asset(algod_client, deployer.address, deployer.private_key, "RUG Token", "RUG")
    dev_id = create_asset(algod_client, deployer.address, deployer.private_key, "DEV Token", "DEV")
    
    logger.info(f"Done! RUG_ID={rug_id}, DEV_ID={dev_id}")

if __name__ == "__main__":
    main()
