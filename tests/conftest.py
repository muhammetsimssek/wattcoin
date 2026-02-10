import pytest
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from bridge_web import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = False
    
    # Set required test env vars
    os.environ['DISCORD_WEBHOOK_URL'] = 'https://discord.com/api/webhooks/test/test'
    os.environ['SOLANA_RPC_URL'] = 'https://api.mainnet-beta.solana.com'
    os.environ['WATT_TOKEN_MINT'] = 'Gpmbh4PoQnL1kNgpMYDED3iv4fczcr7d3qNBLf8rpump'
    
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
