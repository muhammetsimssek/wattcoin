import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_ALERTS_CHANNEL = os.getenv("DISCORD_ALERTS_CHANNEL")
if DISCORD_ALERTS_CHANNEL:
    DISCORD_ALERTS_CHANNEL = int(DISCORD_ALERTS_CHANNEL)

# Use a generic placeholder if not provided, avoiding hardcoded production URLs
WATTCOIN_API_URL = os.getenv("WATTCOIN_API_URL", "https://your-wattcoin-api-url.example.com")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
WATT_MINT_ADDRESS = os.getenv("WATT_MINT_ADDRESS", "Gpmbh4PoQnL1kNgpMYDED3iv4fczcr7d3qNBLf8rpump")

EMBED_COLOR = 0x39ff14  # Green
