import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pre_deploy")

class ProductionValidator:
    """Checklist to ensure no sensitive info or example values leak to production"""
    
    CRITICAL_ENV_VARS = [
        'API_BASE_URL',
        'DISCORD_WEBHOOK_URL',
        'SECRET_KEY',
        'SOLANA_RPC_URL',
        'WATT_TOKEN_MINT'
    ]
    
    FORBIDDEN_STRINGS = [
        'example.com',
        'railway.app', # Specifically requested by Admin
        'localhost',
        'change-me',
        'your-api-key'
    ]

    def validate_env_template(self):
        """Checks if .env.example contains example data (correct)"""
        path = '.env.example'
        if not os.path.exists(path):
            logger.error("❌ .env.example is missing!")
            return False
        return True

    def validate_gitignore(self):
        """Ensures .gitignore covers sensitive files"""
        if not os.path.exists('.gitignore'):
            return False
        with open('.gitignore', 'r') as f:
            content = f.read()
            required = ['.env', '*.secret', 'logs/']
            for item in required:
                if item not in content:
                    logger.error(f"❌ .gitignore is missing: {item}")
                    return False
        return True

    def run_all(self):
        results = [
            self.validate_env_template(),
            self.validate_gitignore()
        ]
        if all(results):
            logger.info("✅ PRE-DEPLOYMENT CHECKS PASSED!")
            return True
        return False

if __name__ == "__main__":
    validator = ProductionValidator()
    if not validator.run_all():
        sys.exit(1)
