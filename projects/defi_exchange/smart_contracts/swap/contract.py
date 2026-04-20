from algopy import ARC4Contract, UInt64, Asset, itxn, gtxn, Global
from algopy.arc4 import abimethod

class Swap(ARC4Contract):
    def __init__(self) -> None:
        self.reserve_a = UInt64(0)
        self.reserve_b = UInt64(0)
        self.token_a = UInt64(0)
        self.token_b = UInt64(0)

    @abimethod()
    def initialize_swap(self, token_a: Asset, token_b: Asset) -> None:
        """Initialize the swap contract with tokens."""
        assert self.token_a == 0, "Already initialized"
        self.token_a = token_a.id
        self.token_b = token_b.id
        
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

    @abimethod()
    def calculate_output(self, amount_in: UInt64, reserve_in: UInt64, reserve_out: UInt64) -> UInt64:
        """K = x * y formula: output_amount = (reserve_out * amount_in) / (reserve_in + amount_in)"""
        assert reserve_in > 0 and reserve_out > 0, "Insufficient liquidity"
        return (reserve_out * amount_in) // (reserve_in + amount_in)

    @abimethod()
    def swap_a_to_b(self, axfer: gtxn.AssetTransferTransaction) -> UInt64:
        """Swap token A for token B."""
        assert axfer.xfer_asset.id == self.token_a, "Invalid asset"
        assert axfer.asset_receiver == Global.current_application_address
        
        amount_in = axfer.asset_amount
        amount_out = self.calculate_output(amount_in, self.reserve_a, self.reserve_b)
        
        assert amount_out > 0, "Swap results in zero output"
        assert amount_out < self.reserve_b, "Insufficient reserve B"
        
        # Update reserves
        self.reserve_a += amount_in
        self.reserve_b -= amount_out
        
        # Transfer token B to sender
        itxn.AssetTransfer(
            xfer_asset=Asset(self.token_b),
            asset_receiver=axfer.sender,
            asset_amount=amount_out,
        ).submit()
        
        return amount_out

    @abimethod()
    def swap_b_to_a(self, axfer: gtxn.AssetTransferTransaction) -> UInt64:
        """Swap token B for token A."""
        assert axfer.xfer_asset.id == self.token_b, "Invalid asset"
        assert axfer.asset_receiver == Global.current_application_address
        
        amount_in = axfer.asset_amount
        amount_out = self.calculate_output(amount_in, self.reserve_b, self.reserve_a)
        
        assert amount_out > 0, "Swap results in zero output"
        assert amount_out < self.reserve_a, "Insufficient reserve A"
        
        # Update reserves
        self.reserve_b += amount_in
        self.reserve_a -= amount_out
        
        # Transfer token A to sender
        itxn.AssetTransfer(
            xfer_asset=Asset(self.token_a),
            asset_receiver=axfer.sender,
            asset_amount=amount_out,
        ).submit()
        
        return amount_out

    @abimethod()
    def update_reserves(self, res_a: UInt64, res_b: UInt64) -> None:
        """Allow pool to sync reserves with swap engine (Simplified for modular demo)."""
        # In a real system, this would be restricted to the admin or AMM pool contract
        self.reserve_a = res_a
        self.reserve_b = res_b
