import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)

class SolanaWattClient:
    def __init__(self, rpc_url: str, mint_address: str):
        self.rpc_url = rpc_url
        self.timeout = 10.0 # seconds
        
        # ✅ FIXED: Initialize mint address as Pubkey object
        try:
            self.mint_address = Pubkey.from_string(mint_address)
            logger.info(f"Solana client initialized for mint: {mint_address}")
        except Exception as e:
            logger.error(f"Invalid mint address {mint_address}: {e}")
            raise ValueError(f"Invalid WATT token mint address: {mint_address}")

    async def get_watt_balance(self, wallet_address: str) -> float:
        """
        [FIXED] Admin feedback: Proper timeout handling and object-based TokenAccountOpts.
        """
        try:
            owner_pubkey = Pubkey.from_string(wallet_address)
        except Exception as e:
            logger.error(f"Invalid wallet address {wallet_address}: {e}")
            raise ValueError(f"Invalid Solana address: {wallet_address}")

        # ✅ FIXED: Correct timeout usage in context manager
        async with AsyncClient(
            self.rpc_url, 
            commitment=Confirmed, 
            timeout=self.timeout
        ) as client:
            try:
                # Admin feedback: TokenAccountOpts must be object
                opts = TokenAccountOpts(mint=self.mint_address)
                
                # asyncio.wait_for for extra safety layer
                response = await asyncio.wait_for(
                    client.get_token_accounts_by_owner(owner_pubkey, opts),
                    timeout=self.timeout
                )
                
                if not response.value:
                    logger.warning(f"No WATT token account found for {wallet_address}")
                    return 0.0

                # Extract and parse balance
                token_account = response.value[0]
                balance_data = token_account.account.data.parsed['info']['tokenAmount']
                balance = int(balance_data['amount']) / (10 ** balance_data['decimals'])
                
                logger.info(f"Fetched balance for {wallet_address}: {balance} WATT")
                return float(balance)

            except asyncio.TimeoutError:
                logger.error(f"Solana RPC timeout ({self.timeout}s) for {wallet_address}")
                raise ConnectionError(f"RPC request timed out after {self.timeout} seconds")
            except Exception as e:
                logger.error(f"Solana RPC error for {wallet_address}: {e}", exc_info=True)
                raise ConnectionError(f"Failed to fetch balance: {str(e)}")
