# Cell 7: Fetch npm Download Statistics
# Fetches download counts for npm packages

def fetch_npm_downloads_range(packages: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """
    Fetch daily download counts for multiple npm packages.
    Uses bulk API (up to 128 packages per request).
    """
    results = {}

    # Process in batches of 128
    batch_size = 128
    for i in range(0, len(packages), batch_size):
        batch = packages[i:i+batch_size]
        package_list = ",".join(batch)

        url = f"{NPM_DOWNLOADS_API}/range/{start_date}:{end_date}/{package_list}"
        response = safe_request(url, delay=NPM_RATE_LIMIT_DELAY)

        if not response:
            continue

        # Handle both single and bulk response formats
        if isinstance(response, dict):
            if "downloads" in response and "package" in response:
                # Single package response
                pkg_name = response["package"]
                results[pkg_name] = pd.DataFrame(response["downloads"])
            else:
                # Bulk response - keys are package names
                for pkg_name, pkg_data in response.items():
                    if pkg_data and "downloads" in pkg_data:
                        results[pkg_name] = pd.DataFrame(pkg_data["downloads"])

    return results

def fetch_npm_downloads_point(packages: List[str], period: str = "last-week") -> Dict[str, int]:
    """Fetch point-in-time download counts (more reliable for totals)."""
    results = {}

    # Process in batches
    batch_size = 128
    for i in range(0, len(packages), batch_size):
        batch = packages[i:i+batch_size]
        package_list = ",".join(batch)

        url = f"{NPM_DOWNLOADS_API}/point/{period}/{package_list}"
        response = safe_request(url, delay=NPM_RATE_LIMIT_DELAY)

        if not response:
            continue

        if isinstance(response, dict):
            if "downloads" in response and "package" in response:
                # Single package response
                results[response["package"]] = response["downloads"]
            else:
                # Bulk response
                for pkg_name, pkg_data in response.items():
                    if pkg_data and "downloads" in pkg_data:
                        results[pkg_name] = pkg_data["downloads"]

    return results

# Collect all npm packages to track
print("Collecting npm packages to track...")

npm_packages = []

# Official SDK
npm_packages.append("@modelcontextprotocol/sdk")

# From servers
for _, row in servers_master_df.iterrows():
    pkg = row.get("npm_package")
    if pd.notna(pkg) and pkg and pkg not in npm_packages:
        npm_packages.append(pkg)

# Remove duplicates and None values
npm_packages = [p for p in npm_packages if p and isinstance(p, str)]
npm_packages = list(set(npm_packages))

print(f"Tracking {len(npm_packages)} npm packages")
print(f"Sample packages: {npm_packages[:10]}")

# Fetch weekly downloads
print("\nFetching npm weekly downloads...")
npm_weekly = fetch_npm_downloads_point(npm_packages, "last-week")
print(f"✓ Got weekly data for {len(npm_weekly)} packages")

# Fetch daily range for time series
print("\nFetching npm daily download history...")
npm_daily = fetch_npm_downloads_range(npm_packages, START_DATE_90D, END_DATE)
print(f"✓ Got daily data for {len(npm_daily)} packages")

# Create summary DataFrame
npm_summary_list = []
for pkg_name in npm_packages:
    summary = {
        "package_name": pkg_name,
        "package_type": "npm",
        "downloads_last_week": npm_weekly.get(pkg_name, 0)
    }

    # Calculate from daily data
    if pkg_name in npm_daily:
        daily_df = npm_daily[pkg_name]
        if len(daily_df) > 0 and "downloads" in daily_df.columns:
            summary["downloads_30d"] = daily_df.tail(30)["downloads"].sum()
            summary["downloads_90d"] = daily_df["downloads"].sum()
            summary["avg_daily_downloads"] = daily_df["downloads"].mean()

    npm_summary_list.append(summary)

npm_summary_df = pd.DataFrame(npm_summary_list)

# Show top packages
print("\nTop 10 npm packages by weekly downloads:")
display(npm_summary_df.nlargest(10, "downloads_last_week")[["package_name", "downloads_last_week", "downloads_30d"]])

# Create time series DataFrame for charts
npm_timeseries_list = []
for pkg_name, daily_df in npm_daily.items():
    if len(daily_df) > 0:
        daily_df = daily_df.copy()
        daily_df["package_name"] = pkg_name
        npm_timeseries_list.append(daily_df)

if npm_timeseries_list:
    npm_timeseries_df = pd.concat(npm_timeseries_list, ignore_index=True)
    npm_timeseries_df["day"] = pd.to_datetime(npm_timeseries_df["day"])
    print(f"\n✓ Created time series with {len(npm_timeseries_df)} daily records")
else:
    npm_timeseries_df = pd.DataFrame(columns=["day", "downloads", "package_name"])
