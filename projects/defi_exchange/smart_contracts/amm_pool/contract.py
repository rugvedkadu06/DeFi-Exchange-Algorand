from algopy import ARC4Contract, UInt64, Asset, itxn, gtxn, Global
from algopy.arc4 import abimethod

class AmmPool(ARC4Contract):
    def __init__(self) -> None:
        self.token_a_id = UInt64(0)
        self.token_b_id = UInt64(0)
        self.reserve_a = UInt64(0)
        self.reserve_b = UInt64(0)
        self.lp_token_id = UInt64(0)
        self.lp_token_supply = UInt64(0)

    @abimethod()
    def create_pool(self, token_a: Asset, token_b: Asset) -> UInt64:
        """Initialize the pool with two tokens and create LP token."""
        assert self.token_a_id == 0, "Pool already initialized"
        
        self.token_a_id = token_a.id
        self.token_b_id = token_b.id
        
        # Opt-in to tokens
        itxn.AssetTransfer(
            xfer_asset=token_a,
            asset_receiver=Global.current_application_address,
            asset_amount=0,
        ).submit()
        itxn.AssetTransfer(
            xfer_asset=token_b,
            asset_receiver=Global.current_application_address,
            asset_amount=0,
        ).submit()
        
        # Create LP token
        lp_asset = itxn.AssetConfig(
            asset_name="DEX-LP-TOKEN",
            unit_name="LP",
            total=10_000_000_000_000, # Large supply
            decimals=6,
            manager=Global.current_application_address,
        ).submit().created_asset
        
        self.lp_token_id = lp_asset.id
        return lp_asset.id

    @abimethod()
    def add_liquidity(self, axfer_a: gtxn.AssetTransferTransaction, axfer_b: gtxn.AssetTransferTransaction) -> UInt64:
        """Deposit tokens and mint LP tokens."""
        assert axfer_a.xfer_asset.id == self.token_a_id, "Invalid token A"
        assert axfer_b.xfer_asset.id == self.token_b_id, "Invalid token B"
        assert axfer_a.asset_receiver == Global.current_application_address
        assert axfer_b.asset_receiver == Global.current_application_address
        
        amt_a = axfer_a.asset_amount
        amt_b = axfer_b.asset_amount
        
        mint_amount: UInt64
        if self.lp_token_supply == 0:
            # Simple initial mint: amount of A
            mint_amount = amt_a
        else:
            # Proportional minting
            mint_a = (amt_a * self.lp_token_supply) // self.reserve_a
            mint_b = (amt_b * self.lp_token_supply) // self.reserve_b
            mint_amount = mint_a if mint_a < mint_b else mint_b
            
        assert mint_amount > 0, "Insufficient liquidity"
        
        self.reserve_a += amt_a
        self.reserve_b += amt_b
        self.lp_token_supply += mint_amount
        
        # Transfer LP tokens to user
        itxn.AssetTransfer(
            xfer_asset=Asset(self.lp_token_id),
            asset_receiver=axfer_a.sender,
            asset_amount=mint_amount,
        ).submit()
        
        return mint_amount

    @abimethod()
    def remove_liquidity(self, lp_axfer: gtxn.AssetTransferTransaction) -> None:
        """Burn LP tokens and withdraw reserves."""
        assert lp_axfer.xfer_asset.id == self.lp_token_id
        assert lp_axfer.asset_receiver == Global.current_application_address
        assert self.lp_token_supply > 0
        
        lp_amt = lp_axfer.asset_amount
        out_a = (lp_amt * self.reserve_a) // self.lp_token_supply
        out_b = (lp_amt * self.reserve_b) // self.lp_token_supply
        
        assert out_a > 0 and out_b > 0, "Insufficient LP tokens for withdrawal"
        
        self.reserve_a -= out_a
        self.reserve_b -= out_b
        self.lp_token_supply -= lp_amt
        
        # Send tokens back to user
        itxn.AssetTransfer(
            xfer_asset=Asset(self.token_a_id),
            asset_receiver=lp_axfer.sender,
            asset_amount=out_a,
        ).submit()
        
        itxn.AssetTransfer(
            xfer_asset=Asset(self.token_b_id),
            asset_receiver=lp_axfer.sender,
            asset_amount=out_b,
        ).submit()

    @abimethod()
    def get_reserves(self) -> tuple[UInt64, UInt64]:
        """Return current pool reserves."""
        return (self.reserve_a, self.reserve_b)
