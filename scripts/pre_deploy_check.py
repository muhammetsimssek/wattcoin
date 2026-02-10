import os
import sys
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("pre_deploy")

class ProductionValidator:
    """Comprehensive pre-deployment validation for WattCoin"""
    
    CRITICAL_ENV_VARS = [
        'DISCORD_WEBHOOK_URL',
        'SOLANA_RPC_URL',
        'WATT_TOKEN_MINT',
        'SECRET_KEY'
    ]
    
    FORBIDDEN_PATTERNS = [
        r'example\.com',
        r'railway\.app', 
        r'localhost',
        r'127\.0\.0\.1',
        r'change-me',
        r'your-api-key'
    ]

    def validate_env_vars(self):
        """Check required production env vars"""
        logger.info("Validating environment variables...")
        missing = [v for v in self.CRITICAL_ENV_VARS if not os.getenv(v)]
        if missing:
            logger.error(f"❌ Missing critical env vars: {missing}")
            return False
        return True

    def validate_no_leaks(self):
        """Ensure no dev values in critical env vars"""
        logger.info("Checking for config leaks...")
        for var in self.CRITICAL_ENV_VARS:
            val = os.getenv(var, '')
            for pattern in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, val.lower()):
                    logger.error(f"❌ {var} contains forbidden pattern: {pattern}")
                    return False
        return True

    def validate_file_structure(self):
        """Verify existence of core files"""
        logger.info("Validating file structure...")
        required = ['.env.example', '.gitignore', 'requirements.txt', 'bridge_web.py']
        for f in required:
            if not os.path.exists(f):
                logger.error(f"❌ Missing file: {f}")
                return False
        return True

    def run_all(self):
        logger.info("="*60)
        logger.info("Starting WattCoin Pre-Deployment Audit")
        logger.info("="*60)
        results = [
            self.validate_env_vars(),
            self.validate_no_leaks(),
            self.validate_file_structure()
        ]
        if all(results):
            logger.info("="*60)
            logger.info("✅ ALL PRE-DEPLOYMENT CHECKS PASSED!")
            logger.info("="*60)
            return True
        return False

if __name__ == "__main__":
    validator = ProductionValidator()
    if not validator.run_all():
        sys.exit(1)
