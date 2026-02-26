# Cell 9: Join All Data into Unified Server Table
# Merges server info with GitHub metrics and download stats

print("Joining all data sources...")

# Start with master server list
servers_enriched_df = servers_master_df.copy()

# Join GitHub metrics
if 'github_metrics_df' in dir() and len(github_metrics_df) > 0:
    # Select columns to join (avoid duplicates)
    github_cols_to_join = [col for col in github_metrics_df.columns
                          if col not in servers_enriched_df.columns or col == "server_id"]

    servers_enriched_df = servers_enriched_df.merge(
        github_metrics_df[github_cols_to_join],
        on="server_id",
        how="left"
    )
    print(f"  ✓ Joined GitHub metrics")

# Create package-to-server mapping
server_npm_map = servers_enriched_df[["server_id", "npm_package"]].dropna(subset=["npm_package"])
server_npm_map = dict(zip(server_npm_map["npm_package"], server_npm_map["server_id"]))

server_pypi_map = servers_enriched_df[["server_id", "pypi_package"]].dropna(subset=["pypi_package"])
server_pypi_map = dict(zip(server_pypi_map["pypi_package"], server_pypi_map["server_id"]))

# Join npm downloads
if 'npm_summary_df' in dir() and len(npm_summary_df) > 0:
    npm_with_server = npm_summary_df.copy()
    npm_with_server["server_id"] = npm_with_server["package_name"].map(server_npm_map)

    # Rename columns to avoid conflicts
    npm_cols = {
        "downloads_last_week": "npm_downloads_week",
        "downloads_30d": "npm_downloads_30d",
        "downloads_90d": "npm_downloads_90d",
        "avg_daily_downloads": "npm_avg_daily"
    }

    for old_col, new_col in npm_cols.items():
        if old_col in npm_with_server.columns:
            npm_with_server[new_col] = npm_with_server[old_col]

    npm_join_cols = ["server_id"] + list(npm_cols.values())
    npm_join_cols = [c for c in npm_join_cols if c in npm_with_server.columns]

    npm_to_join = npm_with_server[npm_with_server["server_id"].notna()][npm_join_cols]
    servers_enriched_df = servers_enriched_df.merge(npm_to_join, on="server_id", how="left")
    print(f"  ✓ Joined npm download stats")

# Join PyPI downloads
if 'pypi_summary_df' in dir() and len(pypi_summary_df) > 0:
    pypi_with_server = pypi_summary_df.copy()
    pypi_with_server["server_id"] = pypi_with_server["package_name"].map(server_pypi_map)

    # Rename columns
    pypi_cols = {
        "downloads_last_week": "pypi_downloads_week",
        "downloads_last_month": "pypi_downloads_month",
        "downloads_last_day": "pypi_downloads_day"
    }

    for old_col, new_col in pypi_cols.items():
        if old_col in pypi_with_server.columns:
            pypi_with_server[new_col] = pypi_with_server[old_col]

    pypi_join_cols = ["server_id"] + list(pypi_cols.values())
    pypi_join_cols = [c for c in pypi_join_cols if c in pypi_with_server.columns]

    pypi_to_join = pypi_with_server[pypi_with_server["server_id"].notna()][pypi_join_cols]
    servers_enriched_df = servers_enriched_df.merge(pypi_to_join, on="server_id", how="left")
    print(f"  ✓ Joined PyPI download stats")

# Calculate combined downloads
servers_enriched_df["total_downloads_week"] = (
    servers_enriched_df.get("npm_downloads_week", pd.Series([0]*len(servers_enriched_df))).fillna(0) +
    servers_enriched_df.get("pypi_downloads_week", pd.Series([0]*len(servers_enriched_df))).fillna(0)
)

print(f"\n✓ Created enriched server table with {len(servers_enriched_df)} servers")
print(f"  Columns: {list(servers_enriched_df.columns)}")

# Show sample
display(servers_enriched_df[[
    "name", "author", "github_stars", "npm_downloads_week", "pypi_downloads_week", "total_downloads_week"
]].dropna(subset=["github_stars"]).head(10))
