# Cell 16: Automation & Manual Input Configuration
# Set up scheduled refresh and manual server input

# ============================================
# HEX SCHEDULE CONFIGURATION
# ============================================

"""
To enable scheduled refresh in Hex:

1. Click the "Schedule" button in the top right of your Hex app
2. Configure the schedule:
   - Frequency: Daily or Weekly
   - Time: Off-peak hours (e.g., 6 AM UTC)
   - Timezone: UTC recommended

3. Set up notifications:
   - Enable email notifications on failure
   - Optionally notify on success

4. Consider incremental refresh:
   - The GitHub API has rate limits
   - Consider running full refresh weekly
   - Run download stats daily

Note: Hex free tier allows 1 scheduled run per day.
Professional tier allows unlimited schedules.
"""

print("📅 Schedule Configuration")
print("-" * 40)
print("Recommended schedule:")
print("  • Full refresh: Weekly (Sundays at 6 AM UTC)")
print("  • Downloads only: Daily (6 AM UTC)")
print("-" * 40)

# ============================================
# MANUAL SERVER INPUT (Hex Input Table)
# ============================================

"""
In Hex, create an Input Table component for manual server additions:

1. Add a new "Input Table" component
2. Configure columns:
   - name (text, required)
   - repository (url, required)
   - npm_package (text, optional)
   - pypi_package (text, optional)
   - company (text, optional)
   - category (text, optional)

3. Name the input table: manual_servers_input

4. Reference it in the pipeline:
   if 'manual_servers_input' in dir():
       curated_servers.extend(manual_servers_input.to_dict('records'))
"""

# Example structure for manual input
MANUAL_SERVER_SCHEMA = {
    "columns": [
        {"name": "name", "type": "text", "required": True, "description": "Server display name"},
        {"name": "repository", "type": "url", "required": True, "description": "GitHub repository URL"},
        {"name": "npm_package", "type": "text", "required": False, "description": "npm package name"},
        {"name": "pypi_package", "type": "text", "required": False, "description": "PyPI package name"},
        {"name": "company", "type": "text", "required": False, "description": "Company/organization"},
        {"name": "category", "type": "text", "required": False, "description": "Comma-separated categories"}
    ]
}

print("\n📝 Manual Server Input Schema:")
for col in MANUAL_SERVER_SCHEMA["columns"]:
    req = "required" if col["required"] else "optional"
    print(f"  • {col['name']} ({col['type']}, {req}): {col['description']}")

# ============================================
# EXPORT DATA FOR EXTERNAL USE
# ============================================

print("\n📤 Export Options")
print("-" * 40)

# Prepare export datasets
exports = {
    "servers_master": servers_enriched_df,
    "ecosystem_kpis": ecosystem_kpis_df,
    "npm_downloads_timeseries": npm_timeseries_df if 'npm_timeseries_df' in dir() else pd.DataFrame(),
    "pypi_downloads_timeseries": pypi_timeseries_df if 'pypi_timeseries_df' in dir() else pd.DataFrame()
}

for name, df in exports.items():
    print(f"  • {name}: {len(df)} rows")

# In Hex, these can be exported as:
# 1. Download as CSV/Excel from the table view
# 2. Connect to a data warehouse (Snowflake, BigQuery, etc.)
# 3. Use the Hex API to fetch data programmatically

# ============================================
# GITHUB TOKEN CONFIGURATION
# ============================================

print("\n🔑 GitHub Token Setup")
print("-" * 40)
print("""
To increase GitHub API rate limits:

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens
   - Generate a new token with 'public_repo' scope
   - Copy the token

2. Add to Hex Secrets:
   - In your Hex project, click the lock icon (Secrets)
   - Add a new secret named 'GITHUB_TOKEN'
   - Paste your token value

3. Reference in Cell 1:
   GITHUB_TOKEN = hex_secrets.get("GITHUB_TOKEN", None)

Rate limits:
   - Without token: 60 requests/hour
   - With token: 5,000 requests/hour
""")

# ============================================
# DATA FRESHNESS INDICATOR
# ============================================

print("\n🕐 Data Freshness")
print("-" * 40)
print(f"  Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Data range: {START_DATE_90D} to {END_DATE}")

# Create freshness indicator for dashboard
data_freshness = {
    "last_refresh": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data_start_date": START_DATE_90D,
    "data_end_date": END_DATE,
    "servers_count": len(servers_enriched_df),
    "refresh_status": "Success"
}

print(f"\n✅ Dashboard ready with {len(servers_enriched_df)} servers")
