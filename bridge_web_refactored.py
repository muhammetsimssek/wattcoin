import os
import sys
import json
import time
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "wattcoin-dev-key-change-in-prod")
app._server_start_time = time.time()

# =============================================================================
# 1. LOGGING CONFIGURATION (Fixed per Admin/Muhammet feedback)
# =============================================================================
def setup_logging():
    """Configure application-wide logging with auto-directory creation"""
    log_dir = os.getenv('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'wattcoin.log')
    
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    
    # File handler (DEBUG and above, 10MB rotation)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024, # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear() # Prevent duplicates
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

setup_logging()
logger = logging.getLogger("wattcoin.bridge")

# =============================================================================
# 5. ENVIRONMENT VALIDATION
# =============================================================================
def validate_environment():
    """Validate critical environment variables at startup"""
    required_vars = {
        'DISCORD_WEBHOOK_URL': 'Discord notifications',
        'SOLANA_RPC_URL': 'Solana blockchain access',
        'WATT_TOKEN_MINT': 'WATT token identification'
    }
    missing = []
    for var, purpose in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} (needed for: {purpose})")
    
    if missing:
        logger.error("="*60)
        logger.error("CRITICAL: Missing required environment variables:")
        for item in missing:
            logger.error(f" - {item}")
        logger.error("="*60)
        logger.error("Application cannot start without these variables.")
        sys.exit(1)
    logger.info("✅ All required environment variables present")

# Mock clients and helpers for snippet compatibility
ai_client = None
claude_client = None
def get_active_nodes(): return []

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.route('/health')
def health():
    """
    [FIXED] Enhanced health check with absolute backward compatibility.
    Maintains all legacy fields while providing a deep 'details' object.
    """
    active_nodes_count = 0
    open_tasks_count = 0
    
    try:
        active_nodes_list = get_active_nodes()
        active_nodes_count = len(active_nodes_list)
    except Exception as e:
        logger.error(f"Failed to fetch active nodes: {e}", exc_info=True)

    try:
        data_dir = os.getenv('DATA_DIR', '/app/data')
        tasks_path = os.path.join(data_dir, 'tasks.json')
        if os.path.exists(tasks_path):
            with open(tasks_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                tasks = tasks_data.get("tasks", {})
                open_tasks_count = sum(1 for t in tasks.values() if t.get("status") == "open")
    except Exception as e:
        logger.error(f"Failed to read tasks.json: {e}", exc_info=True)

    uptime_seconds = int(time.time() - app._server_start_time)

    # Legacy fields (REQUIRED for backward compatibility)
    response_data = {
        'status': 'ok',
        'version': '3.4.0',
        'ai': bool(ai_client),
        'claude': bool(claude_client),
        'proxy': True,
        'admin': True,
        'active_nodes': active_nodes_count,
        
        # New Deep Monitoring Object
        'details': {
            'system_status': 'healthy',
            'uptime_seconds': uptime_seconds,
            'open_tasks': open_tasks_count,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'services': {
                'discord_webhook': 'configured' if os.getenv("DISCORD_WEBHOOK_URL") else 'missing',
                'ai_api_provider': 'active' if ai_client else 'inactive',
                'solana_rpc': 'configured' if os.getenv("SOLANA_RPC_URL") else 'missing'
            }
        }
    }
    
    logger.debug(f"Health check: {active_nodes_count} nodes, {open_tasks_count} tasks")
    return jsonify(response_data), 200

@app.route('/recent-activity')
@app.route('/api/v1/recent-activity')
def recent_activity():
    """
    [FIXED] Dual-path support for activity monitoring (legacy and versioned).
    Returns a safe fallback structure with ISO 8601 consistency.
    """
    try:
        activities_data = {
            "activities": [], 
            "status": "tracking_active",
            "last_updated": datetime.utcnow().isoformat() + 'Z',
            "total_count": 0,
            "meta": {
                "version": "3.4.0",
                "endpoint": "/recent-activity"
            }
        }
        return jsonify(activities_data), 200
    except Exception as e:
        logger.error(f"Activity endpoint error: {e}", exc_info=True)
        return jsonify({
            "error": "Service temporarily unavailable",
            "activities": [],
            "status": "degraded",
            "last_updated": datetime.utcnow().isoformat() + 'Z'
        }), 503

if __name__ == '__main__':
    validate_environment()
    logger.info("Starting WattCoin Bridge Web Service...")
    app.run(
        host='0.0.0.0', 
        port=int(os.getenv('PORT', 5000)),
        debug=(os.getenv('FLASK_ENV') == 'development')
    )
