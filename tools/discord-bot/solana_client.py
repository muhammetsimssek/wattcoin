import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from config import SOLANA_RPC_URL, WATT_MINT_ADDRESS

logger = logging.getLogger('wattcoin-bot')

class SolanaClient:
    def __init__(self):
        self.rpc_url = SOLANA_RPC_URL
        self.timeout = 10.0
        try:
            self.mint_address = Pubkey.from_string(WATT_MINT_ADDRESS)
        except Exception as e:
            logger.error(f"Invalid WATT_MINT_ADDRESS: {e}")
            raise

    async def get_watt_balance(self, wallet_address: str):
        """
        Fetches WATT balance with robust error handling and proper Solana-py types.
        """
        try:
            owner_pubkey = Pubkey.from_string(wallet_address)
        except ValueError:
            logger.error(f"Invalid wallet address format: {wallet_address}")
            return None

        async with AsyncClient(self.rpc_url, commitment=Confirmed, timeout=self.timeout) as client:
            try:
                # FIXED: TokenAccountOpts must be an object, not a dict
                opts = TokenAccountOpts(mint=self.mint_address)
                
                # Fetch token accounts
                response = await asyncio.wait_for(
                    client.get_token_accounts_by_owner(owner_pubkey, opts),
                    timeout=self.timeout
                )
                
                if not response.value:
                    return 0.0

                total_balance = 0.0
                for account in response.value:
                    # Fetch balance for each account found
                    balance_resp = await client.get_token_account_balance(account.pubkey)
                    if balance_resp.value:
                        total_balance += float(balance_resp.value.ui_amount)
                
                return total_balance
            except asyncio.TimeoutError:
                logger.error(f"Solana RPC timeout for {wallet_address}")
                return None
            except Exception as e:
                logger.error(f"Error fetching Solana balance for {wallet_address}: {e}")
                return None
