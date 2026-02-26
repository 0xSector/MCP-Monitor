# Cell 1: Configuration and Imports
# This cell sets up all dependencies and configuration for the MCP Ecosystem Dashboard

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import json

# ============================================
# CONFIGURATION
# ============================================

# API Endpoints
MCP_REGISTRY_BASE = "https://registry.modelcontextprotocol.io/v0"
GITHUB_API_BASE = "https://api.github.com"
NPM_DOWNLOADS_API = "https://api.npmjs.org/downloads"

# GitHub token (set as Hex secret or environment variable)
# GITHUB_TOKEN = hex_secrets.get("GITHUB_TOKEN", None)  # Uncomment in Hex
GITHUB_TOKEN = None  # Placeholder - set in Hex secrets

# Rate limiting settings
GITHUB_RATE_LIMIT_DELAY = 2.5  # seconds between requests (30 req/min unauthenticated)
NPM_RATE_LIMIT_DELAY = 0.5

# Date ranges
END_DATE = datetime.now().strftime("%Y-%m-%d")
START_DATE_90D = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
START_DATE_30D = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

# Helper function for API requests
def safe_request(url: str, headers: Dict = None, params: Dict = None, delay: float = 0) -> Optional[Dict]:
    """Make a safe API request with error handling and optional delay."""
    if delay > 0:
        time.sleep(delay)

    try:
        default_headers = {"Accept": "application/json"}
        if GITHUB_TOKEN and "github.com" in url:
            default_headers["Authorization"] = f"token {GITHUB_TOKEN}"
        if headers:
            default_headers.update(headers)

        response = requests.get(url, headers=default_headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

print("✓ Configuration loaded")
print(f"  Date range: {START_DATE_90D} to {END_DATE}")
print(f"  GitHub token: {'Configured' if GITHUB_TOKEN else 'Not set (rate limits apply)'}")
