# ============================================================
# MCP ECOSYSTEM ADOPTION DASHBOARD - COMPLETE HEX NOTEBOOK
# ============================================================
#
# This file contains all cells for the MCP Ecosystem Dashboard.
# Import into Hex and separate cells at the "# Cell X:" comments.
#
# Dashboard Pages:
#   1. Ecosystem Overview - KPIs, top servers, category distribution
#   2. Server Discovery Table - Searchable/filterable server list
#   3. Server Deep Dive - Individual server metrics
#   4. Trends & Velocity - SDK trends, ecosystem growth
#
# Data Sources:
#   - MCP Registry API
#   - GitHub Search & Repo API
#   - npm Downloads API
#   - PyPI Stats API
#   - Curated server list
#
# ============================================================

# ============================================================
# Cell 1: Configuration and Imports
# ============================================================

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import json

# API Endpoints
MCP_REGISTRY_BASE = "https://registry.modelcontextprotocol.io/v0"
GITHUB_API_BASE = "https://api.github.com"
NPM_DOWNLOADS_API = "https://api.npmjs.org/downloads"
PYPISTATS_API = "https://pypistats.org/api"

# GitHub token - SET IN HEX SECRETS
# GITHUB_TOKEN = hex_secrets.get("GITHUB_TOKEN", None)  # Uncomment in Hex
GITHUB_TOKEN = None  # Add your token here or use Hex secrets

# Rate limiting (faster with token: 5000 req/hr)
GITHUB_RATE_LIMIT_DELAY = 0.3
NPM_RATE_LIMIT_DELAY = 0.5

# Date ranges - use fixed dates for npm API compatibility
# npm API only has historical data, so use recent past dates
END_DATE = "2025-02-20"
START_DATE_90D = "2024-11-22"
START_DATE_30D = "2025-01-21"

# Color palette
COLORS = {
    "primary": "#2563eb",
    "secondary": "#0891b2",
    "accent": "#7c3aed",
    "success": "#059669",
    "warning": "#d97706",
    "neutral": "#6b7280"
}
CHART_TEMPLATE = "plotly_white"

def safe_request(url: str, headers: Dict = None, params: Dict = None, delay: float = 0) -> Optional[Dict]:
    """Make a safe API request with error handling."""
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

print("[OK] Configuration loaded")

# ============================================================
# Cell 2: Fetch MCP Registry Servers
# ============================================================

def fetch_mcp_registry_servers(limit_per_page: int = 100, max_pages: int = 50) -> pd.DataFrame:
    """Fetch all servers from MCP Registry with pagination."""
    all_servers = []
    cursor = None
    page = 0

    while page < max_pages:
        params = {"limit": limit_per_page}
        if cursor:
            params["cursor"] = cursor

        response = safe_request(f"{MCP_REGISTRY_BASE}/servers", params=params)
        if not response:
            break

        servers = response.get("servers", response.get("items", []))
        if not servers:
            break

        for server in servers:
            package_info = server.get("package", {})
            npm_pkg = package_info.get("npm") if isinstance(package_info, dict) else None
            pypi_pkg = package_info.get("pypi") if isinstance(package_info, dict) else None

            repo = server.get("repository", server.get("repo", ""))
            if isinstance(repo, dict):
                repo = repo.get("url", "")

            all_servers.append({
                "server_id": server.get("id", server.get("name", "")),
                "name": server.get("name", ""),
                "description": (server.get("description", "") or "")[:500],
                "repository": repo,
                "npm_package": npm_pkg,
                "pypi_package": pypi_pkg,
                "categories": ",".join(server.get("categories", [])) if isinstance(server.get("categories"), list) else "",
                "author": server.get("author", ""),
                "version": server.get("version", ""),
                "source": "mcp_registry",
                "discovered_date": datetime.now().strftime("%Y-%m-%d")
            })

        cursor = response.get("next_cursor")
        if not cursor:
            break
        page += 1

    return pd.DataFrame(all_servers)

print("Fetching MCP Registry servers...")
registry_servers_df = fetch_mcp_registry_servers()
print(f"[OK] Found {len(registry_servers_df)} servers in MCP Registry")

# ============================================================
# Cell 3: GitHub Discovery
# ============================================================

def github_search_repos(query: str, max_results: int = 100) -> List[Dict]:
    """Search GitHub repos with pagination."""
    repos = []
    per_page = min(100, max_results)

    for page in range(1, (max_results // per_page) + 2):
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page, "page": page}
        response = safe_request(f"{GITHUB_API_BASE}/search/repositories", params=params, delay=GITHUB_RATE_LIMIT_DELAY)
        if not response or "items" not in response:
            break
        repos.extend(response["items"])
        if len(response["items"]) < per_page:
            break

    return repos[:max_results]

SEARCH_QUERIES = ["topic:mcp", "topic:model-context-protocol", '"mcp server" in:readme', "mcp-server in:name"]

print("Searching GitHub for MCP repositories...")
all_github_repos = []
seen_repo_ids = set()

for query in SEARCH_QUERIES:
    print(f"  Searching: {query}")
    repos = github_search_repos(query, max_results=100)

    for repo in repos:
        repo_id = repo.get("id")
        if repo_id not in seen_repo_ids:
            seen_repo_ids.add(repo_id)
            language = (repo.get("language") or "").lower()
            name = (repo.get("name") or "").lower()

            all_github_repos.append({
                "server_id": f"github_{repo_id}",
                "name": repo.get("name", ""),
                "description": (repo.get("description", "") or "")[:500],
                "repository": repo.get("html_url", ""),
                "npm_package": name if language in ["typescript", "javascript"] and "mcp" in name else None,
                "pypi_package": name.replace("-", "_") if language == "python" and "mcp" in name else None,
                "categories": ",".join(repo.get("topics", [])),
                "author": repo.get("owner", {}).get("login", ""),
                "version": "",
                "source": "github_search",
                "discovered_date": datetime.now().strftime("%Y-%m-%d"),
                "github_stars": repo.get("stargazers_count", 0),
                "github_forks": repo.get("forks_count", 0),
                "github_open_issues": repo.get("open_issues_count", 0),
                "github_language": repo.get("language", ""),
                "github_updated_at": repo.get("updated_at", ""),
                "github_created_at": repo.get("created_at", "")
            })

github_discovered_df = pd.DataFrame(all_github_repos)
print(f"[OK] Discovered {len(github_discovered_df)} repos from GitHub search")

# Filter to only repos with "mcp" in the name (excludes large projects with MCP integrations)
github_discovered_df = github_discovered_df[
    github_discovered_df["name"].str.lower().str.contains("mcp", na=False)
]
print(f"[OK] Filtered to {len(github_discovered_df)} MCP-specific repos")

# ============================================================
# Cell 4: Curated Server List
# ============================================================

CURATED_SERVERS = [
    {"name": "Stripe MCP Server", "repository": "https://github.com/stripe/agent-toolkit", "npm_package": "@stripe/agent-toolkit", "pypi_package": "stripe-agent-toolkit", "company": "Stripe", "category": "payments"},
    {"name": "Cloudflare MCP Server", "repository": "https://github.com/cloudflare/mcp-server-cloudflare", "npm_package": "@cloudflare/mcp-server-cloudflare", "pypi_package": None, "company": "Cloudflare", "category": "infrastructure"},
    {"name": "Sentry MCP Server", "repository": "https://github.com/getsentry/sentry-mcp", "npm_package": None, "pypi_package": "sentry-mcp", "company": "Sentry", "category": "monitoring"},
    {"name": "Neon MCP Server", "repository": "https://github.com/neondatabase/mcp-server-neon", "npm_package": "@neondatabase/mcp-server-neon", "pypi_package": None, "company": "Neon", "category": "database"},
    {"name": "Axiom MCP Server", "repository": "https://github.com/axiomhq/mcp-server-axiom", "npm_package": "@axiomhq/mcp-server-axiom", "pypi_package": None, "company": "Axiom", "category": "observability"},
    {"name": "GitHub MCP Server", "repository": "https://github.com/modelcontextprotocol/servers", "npm_package": "@modelcontextprotocol/server-github", "pypi_package": None, "company": "Anthropic", "category": "devtools"},
    {"name": "Filesystem MCP Server", "repository": "https://github.com/modelcontextprotocol/servers", "npm_package": "@modelcontextprotocol/server-filesystem", "pypi_package": None, "company": "Anthropic", "category": "core"},
]

curated_servers_df = pd.DataFrame(CURATED_SERVERS)
curated_servers_df["server_id"] = curated_servers_df["name"].str.lower().str.replace(" ", "_")
curated_servers_df["description"] = curated_servers_df["company"] + " official MCP server"
curated_servers_df["author"] = curated_servers_df["company"]
curated_servers_df["version"] = ""
curated_servers_df["source"] = "curated"
curated_servers_df["discovered_date"] = datetime.now().strftime("%Y-%m-%d")
curated_servers_df["categories"] = curated_servers_df["category"]

print(f"[OK] Loaded {len(curated_servers_df)} curated servers")

# ============================================================
# Cell 5: Merge and Deduplicate
# ============================================================

def normalize_repo_url(url: str) -> str:
    if not url:
        return ""
    url = url.lower().strip().replace("https://", "").replace("http://", "")
    return url.rstrip("/").replace(".git", "")

common_cols = ["server_id", "name", "description", "repository", "npm_package", "pypi_package", "categories", "author", "version", "source", "discovered_date"]

def ensure_columns(df, cols):
    for col in cols:
        if col not in df.columns:
            df[col] = None
    return df[cols]

all_sources = []
if len(registry_servers_df) > 0:
    all_sources.append(ensure_columns(registry_servers_df.copy(), common_cols))
if len(github_discovered_df) > 0:
    all_sources.append(ensure_columns(github_discovered_df.copy(), common_cols))
if len(curated_servers_df) > 0:
    all_sources.append(ensure_columns(curated_servers_df.copy(), common_cols))

combined_df = pd.concat(all_sources, ignore_index=True)
combined_df["repo_normalized"] = combined_df["repository"].apply(normalize_repo_url)

# Deduplicate by repo URL
servers_master_df = combined_df.drop_duplicates(subset=["repo_normalized"], keep="first")
servers_master_df = servers_master_df.drop(columns=["repo_normalized"])

print(f"[OK] After deduplication: {len(servers_master_df)} unique servers")

# ============================================================
# Cell 6: Fetch GitHub Metrics
# ============================================================

def extract_github_owner_repo(url):
    if not url or "github.com" not in url:
        return None, None
    url = url.replace("https://", "").replace("github.com/", "").rstrip("/").replace(".git", "")
    parts = url.split("/")
    return (parts[0], parts[1]) if len(parts) >= 2 else (None, None)

def fetch_github_repo_metrics(owner, repo):
    data = safe_request(f"{GITHUB_API_BASE}/repos/{owner}/{repo}", delay=GITHUB_RATE_LIMIT_DELAY)
    if not data:
        return None
    return {
        "github_stars": data.get("stargazers_count", 0),
        "github_forks": data.get("forks_count", 0),
        "github_open_issues": data.get("open_issues_count", 0),
        "github_language": data.get("language", ""),
        "github_created_at": data.get("created_at", ""),
        "github_updated_at": data.get("updated_at", ""),
        "github_pushed_at": data.get("pushed_at", ""),
        "github_topics": ",".join(data.get("topics", []))
    }

print("Fetching GitHub metrics...")
github_metrics_list = []

for idx, row in servers_master_df.iterrows():
    owner, repo = extract_github_owner_repo(row.get("repository", ""))
    if not owner:
        github_metrics_list.append({"server_id": row["server_id"], "has_github": False})
        continue

    metrics = fetch_github_repo_metrics(owner, repo)
    if metrics:
        metrics["server_id"] = row["server_id"]
        metrics["has_github"] = True
        github_metrics_list.append(metrics)
    else:
        github_metrics_list.append({"server_id": row["server_id"], "has_github": False})

github_metrics_df = pd.DataFrame(github_metrics_list)
print(f"[OK] Fetched GitHub metrics for {github_metrics_df['has_github'].sum()} repos")

# ============================================================
# Cell 7: Fetch npm Downloads
# ============================================================

def fetch_npm_downloads_point(packages, period="last-week"):
    """Fetch npm downloads one package at a time to avoid bulk API issues."""
    results = {}
    for pkg in packages:
        response = safe_request(f"{NPM_DOWNLOADS_API}/point/{period}/{pkg}", delay=NPM_RATE_LIMIT_DELAY)
        if response and "downloads" in response:
            results[pkg] = response["downloads"]
    return results

def fetch_npm_downloads_range(packages, start_date, end_date):
    """Fetch npm download ranges one package at a time."""
    results = {}
    # Limit to top packages to avoid too many requests
    for pkg in packages[:20]:
        response = safe_request(f"{NPM_DOWNLOADS_API}/range/{start_date}:{end_date}/{pkg}", delay=NPM_RATE_LIMIT_DELAY)
        if response and "downloads" in response:
            results[pkg] = pd.DataFrame(response["downloads"])
    return results

npm_packages = ["@modelcontextprotocol/sdk"]
for _, row in servers_master_df.iterrows():
    if pd.notna(row.get("npm_package")) and row["npm_package"] not in npm_packages:
        npm_packages.append(row["npm_package"])
    if len(npm_packages) >= 30:  # Limit to top 30 to reduce API calls
        break

print(f"Fetching npm downloads for {len(npm_packages)} packages...")
npm_weekly = fetch_npm_downloads_point(npm_packages, "last-week")
npm_daily = fetch_npm_downloads_range(npm_packages, START_DATE_90D, END_DATE)

npm_summary_df = pd.DataFrame([
    {"package_name": pkg, "package_type": "npm", "downloads_last_week": npm_weekly.get(pkg, 0)}
    for pkg in npm_packages
])

print(f"[OK] Got npm data for {len(npm_weekly)} packages")

# ============================================================
# Cell 8: Fetch PyPI Downloads
# ============================================================

def fetch_pypi_downloads_recent(package):
    response = safe_request(f"{PYPISTATS_API}/packages/{package}/recent", delay=0.5)
    if response and "data" in response:
        return response["data"]
    return None

pypi_packages = ["mcp"]
for _, row in servers_master_df.iterrows():
    if pd.notna(row.get("pypi_package")) and row["pypi_package"] not in pypi_packages:
        pypi_packages.append(row["pypi_package"])
    if len(pypi_packages) >= 15:  # Limit to reduce API calls
        break

print(f"Fetching PyPI downloads for {len(pypi_packages)} packages...")
pypi_summary_list = []
for pkg in pypi_packages:
    data = fetch_pypi_downloads_recent(pkg)
    pypi_summary_list.append({
        "package_name": pkg,
        "package_type": "pypi",
        "downloads_last_week": data.get("last_week", 0) if data else 0,
        "downloads_last_month": data.get("last_month", 0) if data else 0
    })

pypi_summary_df = pd.DataFrame(pypi_summary_list)
print(f"[OK] Got PyPI data for {len([s for s in pypi_summary_list if s['downloads_last_week'] > 0])} packages")

# ============================================================
# Cell 9: Join All Data
# ============================================================

servers_enriched_df = servers_master_df.copy()

# Join GitHub metrics
github_cols = [c for c in github_metrics_df.columns if c not in servers_enriched_df.columns or c == "server_id"]
servers_enriched_df = servers_enriched_df.merge(github_metrics_df[github_cols], on="server_id", how="left")

# Map packages to servers
server_npm_map = dict(zip(servers_enriched_df["npm_package"].dropna(), servers_enriched_df[servers_enriched_df["npm_package"].notna()]["server_id"]))
server_pypi_map = dict(zip(servers_enriched_df["pypi_package"].dropna(), servers_enriched_df[servers_enriched_df["pypi_package"].notna()]["server_id"]))

# Join npm downloads
npm_summary_df["server_id"] = npm_summary_df["package_name"].map(server_npm_map)
npm_summary_df["npm_downloads_week"] = npm_summary_df["downloads_last_week"]
npm_to_join = npm_summary_df[npm_summary_df["server_id"].notna()][["server_id", "npm_downloads_week"]]
servers_enriched_df = servers_enriched_df.merge(npm_to_join, on="server_id", how="left")

# Join PyPI downloads
pypi_summary_df["server_id"] = pypi_summary_df["package_name"].map(server_pypi_map)
pypi_summary_df["pypi_downloads_week"] = pypi_summary_df["downloads_last_week"]
pypi_to_join = pypi_summary_df[pypi_summary_df["server_id"].notna()][["server_id", "pypi_downloads_week"]]
servers_enriched_df = servers_enriched_df.merge(pypi_to_join, on="server_id", how="left")

# Calculate totals
servers_enriched_df["total_downloads_week"] = servers_enriched_df["npm_downloads_week"].fillna(0) + servers_enriched_df["pypi_downloads_week"].fillna(0)

print(f"[OK] Created enriched table with {len(servers_enriched_df)} servers")

# ============================================================
# Cell 10: Calculate Derived Metrics
# ============================================================

def calculate_health_score(row):
    score = 0
    if pd.notna(row.get("github_stars")) and row["github_stars"] >= 10:
        score += min(40, row["github_stars"] / 25)
    if row.get("total_downloads_week", 0) >= 100:
        score += min(30, row["total_downloads_week"] / 500)
    if pd.notna(row.get("github_pushed_at")):
        try:
            days = (datetime.now() - pd.to_datetime(row["github_pushed_at"]).replace(tzinfo=None)).days
            if days <= 30:
                score += 30
            elif days <= 90:
                score += 15
        except:
            pass
    return min(100, score)

def categorize_activity(row):
    if pd.notna(row.get("github_pushed_at")):
        try:
            days = (datetime.now() - pd.to_datetime(row["github_pushed_at"]).replace(tzinfo=None)).days
            if days <= 7:
                return "Active"
            elif days <= 30:
                return "Recent"
            elif days <= 90:
                return "Moderate"
            return "Stale"
        except:
            pass
    return "Unknown"

def categorize_popularity(row):
    stars = row.get("github_stars", 0) or 0
    downloads = row.get("total_downloads_week", 0) or 0
    if stars >= 1000 or downloads >= 10000:
        return "Top Tier"
    elif stars >= 100 or downloads >= 1000:
        return "Popular"
    elif stars >= 10 or downloads >= 100:
        return "Growing"
    return "Emerging"

servers_enriched_df["health_score"] = servers_enriched_df.apply(calculate_health_score, axis=1)
servers_enriched_df["activity_level"] = servers_enriched_df.apply(categorize_activity, axis=1)
servers_enriched_df["popularity_tier"] = servers_enriched_df.apply(categorize_popularity, axis=1)
servers_enriched_df["ecosystem"] = servers_enriched_df.apply(
    lambda x: "TypeScript/JS" if pd.notna(x.get("npm_package")) else "Python" if pd.notna(x.get("pypi_package")) else x.get("github_language", "Unknown"),
    axis=1
)

print("[OK] Derived metrics calculated")

# ============================================================
# Cell 11: Ecosystem KPIs
# ============================================================

total_servers = len(servers_enriched_df)
servers_with_npm = servers_enriched_df["npm_package"].notna().sum()
servers_with_pypi = servers_enriched_df["pypi_package"].notna().sum()
total_stars = int(servers_enriched_df["github_stars"].fillna(0).sum())
total_npm_weekly = int(servers_enriched_df["npm_downloads_week"].fillna(0).sum())
total_pypi_weekly = int(servers_enriched_df["pypi_downloads_week"].fillna(0).sum())
sdk_npm_downloads = npm_weekly.get("@modelcontextprotocol/sdk", 0)
sdk_pypi_downloads = pypi_summary_df[pypi_summary_df["package_name"] == "mcp"]["downloads_last_week"].values[0] if len(pypi_summary_df[pypi_summary_df["package_name"] == "mcp"]) > 0 else 0

activity_distribution = servers_enriched_df["activity_level"].value_counts().to_dict()
ecosystem_distribution = servers_enriched_df["ecosystem"].value_counts().to_dict()

# Extract categories
all_categories = []
for cats in servers_enriched_df["categories"].dropna():
    all_categories.extend([c.strip() for c in str(cats).split(",") if c.strip()])
category_counts = pd.Series(all_categories).value_counts().head(15).to_dict()

ecosystem_kpis = {
    "snapshot_date": datetime.now().strftime("%Y-%m-%d"),
    "total_servers": total_servers,
    "servers_with_npm_package": int(servers_with_npm),
    "servers_with_pypi_package": int(servers_with_pypi),
    "total_github_stars": total_stars,
    "total_npm_downloads_weekly": total_npm_weekly,
    "total_pypi_downloads_weekly": total_pypi_weekly,
    "total_downloads_weekly": total_npm_weekly + total_pypi_weekly,
    "sdk_npm_downloads_weekly": sdk_npm_downloads,
    "sdk_pypi_downloads_weekly": sdk_pypi_downloads,
    "active_percentage": round((activity_distribution.get("Active", 0) + activity_distribution.get("Recent", 0)) / total_servers * 100, 1) if total_servers > 0 else 0
}

ecosystem_kpis_df = pd.DataFrame([ecosystem_kpis])

print("\n" + "="*50)
print("MCP ECOSYSTEM KPIs")
print("="*50)
print(f"Total Servers: {total_servers}")
print(f"Total GitHub Stars: {total_stars:,}")
print(f"Weekly Downloads: {total_npm_weekly + total_pypi_weekly:,}")
print(f"SDK Downloads (npm): {sdk_npm_downloads:,}")
print(f"SDK Downloads (PyPI): {sdk_pypi_downloads:,}")
print("="*50)

# ============================================================
# Cell 12-15: Visualizations (See separate cells)
# ============================================================

import plotly.express as px
import plotly.graph_objects as go

# Top servers by stars
top_by_stars = servers_enriched_df.nlargest(10, "github_stars")[["name", "github_stars", "author"]]
fig_stars = px.bar(top_by_stars, x="github_stars", y="name", orientation="h",
                   title="Top 10 MCP Servers by GitHub Stars", color="github_stars",
                   color_continuous_scale="Blues")
fig_stars.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
fig_stars.show()

# Category distribution
if category_counts:
    cat_df = pd.DataFrame([{"category": k, "count": v} for k, v in list(category_counts.items())[:10]])
    fig_cat = px.pie(cat_df, values="count", names="category", title="MCP Server Categories", hole=0.4)
    fig_cat.show()

# Activity distribution
act_df = pd.DataFrame([{"level": k, "count": v} for k, v in activity_distribution.items()])
fig_act = px.bar(act_df, x="level", y="count", title="Server Activity Levels", color="level")
fig_act.show()

print("\n[SUCCESS] MCP Ecosystem Dashboard Complete!")
print(f"   Total Servers: {total_servers}")
print(f"   GitHub Stars: {total_stars:,}")
print(f"   Weekly Downloads: {total_npm_weekly + total_pypi_weekly:,}")
