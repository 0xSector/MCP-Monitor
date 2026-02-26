# Cell 11: Aggregate Ecosystem-Wide KPIs
# Computes high-level metrics for the entire MCP ecosystem

print("Calculating ecosystem KPIs...")

# Current date for snapshot
snapshot_date = datetime.now().strftime("%Y-%m-%d")

# ============================================
# SERVER COUNT METRICS
# ============================================

total_servers = len(servers_enriched_df)
servers_by_source = servers_enriched_df["source"].value_counts().to_dict()

# Servers with packages
servers_with_npm = servers_enriched_df["npm_package"].notna().sum()
servers_with_pypi = servers_enriched_df["pypi_package"].notna().sum()
servers_with_github = servers_enriched_df.get("has_github", pd.Series([False]*len(servers_enriched_df))).sum()

# ============================================
# ACTIVITY METRICS
# ============================================

activity_distribution = servers_enriched_df["activity_level"].value_counts().to_dict()
active_servers = activity_distribution.get("Active", 0) + activity_distribution.get("Recent", 0)
active_percentage = (active_servers / total_servers * 100) if total_servers > 0 else 0

# ============================================
# POPULARITY METRICS
# ============================================

total_stars = servers_enriched_df["github_stars"].fillna(0).sum()
avg_stars = servers_enriched_df["github_stars"].fillna(0).mean()
median_stars = servers_enriched_df["github_stars"].fillna(0).median()

# ============================================
# DOWNLOAD METRICS
# ============================================

# npm downloads
total_npm_weekly = servers_enriched_df["npm_downloads_week"].fillna(0).sum()

# Add SDK downloads separately (if not already in servers)
sdk_npm_downloads = npm_weekly.get("@modelcontextprotocol/sdk", 0) if 'npm_weekly' in dir() else 0

# PyPI downloads
total_pypi_weekly = servers_enriched_df["pypi_downloads_week"].fillna(0).sum()

# Add SDK downloads
sdk_pypi_downloads = 0
if 'pypi_summary_df' in dir():
    mcp_row = pypi_summary_df[pypi_summary_df["package_name"] == "mcp"]
    if len(mcp_row) > 0:
        sdk_pypi_downloads = mcp_row["downloads_last_week"].values[0]

# Combined
total_downloads_weekly = total_npm_weekly + total_pypi_weekly

# ============================================
# CATEGORY METRICS
# ============================================

# Extract categories
all_categories = []
for cats in servers_enriched_df["categories"].dropna():
    if isinstance(cats, str):
        all_categories.extend([c.strip() for c in cats.split(",") if c.strip()])

category_counts = pd.Series(all_categories).value_counts().head(15).to_dict()

# ============================================
# ECOSYSTEM SPLIT
# ============================================

ecosystem_distribution = servers_enriched_df["ecosystem"].value_counts().to_dict()

# ============================================
# CREATE KPI SUMMARY
# ============================================

ecosystem_kpis = {
    "snapshot_date": snapshot_date,

    # Server counts
    "total_servers": total_servers,
    "servers_from_registry": servers_by_source.get("mcp_registry", 0),
    "servers_from_github": servers_by_source.get("github_search", 0),
    "servers_from_curated": servers_by_source.get("curated", 0),

    # Package coverage
    "servers_with_npm_package": servers_with_npm,
    "servers_with_pypi_package": servers_with_pypi,
    "servers_with_github": int(servers_with_github),

    # Activity
    "active_servers": active_servers,
    "active_percentage": round(active_percentage, 1),

    # Popularity
    "total_github_stars": int(total_stars),
    "avg_stars_per_server": round(avg_stars, 1),
    "median_stars": int(median_stars),

    # Downloads
    "total_npm_downloads_weekly": int(total_npm_weekly),
    "total_pypi_downloads_weekly": int(total_pypi_weekly),
    "total_downloads_weekly": int(total_downloads_weekly),
    "sdk_npm_downloads_weekly": int(sdk_npm_downloads),
    "sdk_pypi_downloads_weekly": int(sdk_pypi_downloads),
}

# Create DataFrame for display
kpi_df = pd.DataFrame([ecosystem_kpis]).T.reset_index()
kpi_df.columns = ["Metric", "Value"]

print("\n" + "="*50)
print("MCP ECOSYSTEM KPIs")
print("="*50)
print(f"Snapshot Date: {snapshot_date}")
print("-"*50)

print(f"\n📦 SERVER COUNTS")
print(f"   Total MCP Servers: {total_servers}")
print(f"   From Registry: {servers_by_source.get('mcp_registry', 0)}")
print(f"   From GitHub: {servers_by_source.get('github_search', 0)}")
print(f"   Curated: {servers_by_source.get('curated', 0)}")

print(f"\n⚡ ACTIVITY")
print(f"   Active Servers (last 30 days): {active_servers} ({active_percentage:.1f}%)")

print(f"\n⭐ POPULARITY")
print(f"   Total GitHub Stars: {int(total_stars):,}")
print(f"   Average Stars: {avg_stars:.1f}")

print(f"\n📥 DOWNLOADS (Weekly)")
print(f"   npm Total: {int(total_npm_weekly):,}")
print(f"   PyPI Total: {int(total_pypi_weekly):,}")
print(f"   Combined: {int(total_downloads_weekly):,}")
print(f"   Official SDK (npm): {int(sdk_npm_downloads):,}")
print(f"   Official SDK (PyPI): {int(sdk_pypi_downloads):,}")

print(f"\n🏷️ TOP CATEGORIES")
for cat, count in list(category_counts.items())[:10]:
    print(f"   {cat}: {count}")

print("\n" + "="*50)

# Store for visualizations
ecosystem_kpis_df = pd.DataFrame([ecosystem_kpis])
