# Cell 8: Fetch PyPI Download Statistics
# Uses pypistats.org API for download counts (alternative to BigQuery)

PYPISTATS_API = "https://pypistats.org/api"

def fetch_pypi_downloads_recent(package: str) -> Optional[Dict]:
    """Fetch recent download stats from pypistats.org"""
    url = f"{PYPISTATS_API}/packages/{package}/recent"
    response = safe_request(url, delay=0.5)

    if not response or "data" not in response:
        return None

    data = response["data"]
    return {
        "downloads_last_day": data.get("last_day", 0),
        "downloads_last_week": data.get("last_week", 0),
        "downloads_last_month": data.get("last_month", 0)
    }

def fetch_pypi_downloads_overall(package: str, mirrors: bool = True) -> Optional[pd.DataFrame]:
    """Fetch daily download history from pypistats.org"""
    url = f"{PYPISTATS_API}/packages/{package}/overall"
    params = {"mirrors": str(mirrors).lower()}
    response = safe_request(url, params=params, delay=0.5)

    if not response or "data" not in response:
        return None

    return pd.DataFrame(response["data"])

# Collect all PyPI packages to track
print("Collecting PyPI packages to track...")

pypi_packages = []

# Official Python SDK
pypi_packages.append("mcp")

# From servers
for _, row in servers_master_df.iterrows():
    pkg = row.get("pypi_package")
    if pd.notna(pkg) and pkg and pkg not in pypi_packages:
        pypi_packages.append(pkg)

# Remove duplicates
pypi_packages = [p for p in pypi_packages if p and isinstance(p, str)]
pypi_packages = list(set(pypi_packages))

print(f"Tracking {len(pypi_packages)} PyPI packages")
print(f"Packages: {pypi_packages}")

# Fetch download stats
print("\nFetching PyPI download statistics...")

pypi_summary_list = []
pypi_daily_data = {}

for pkg_name in pypi_packages:
    print(f"  Fetching: {pkg_name}")

    # Get recent summary
    recent = fetch_pypi_downloads_recent(pkg_name)

    if recent:
        summary = {
            "package_name": pkg_name,
            "package_type": "pypi",
            "downloads_last_day": recent.get("downloads_last_day", 0),
            "downloads_last_week": recent.get("downloads_last_week", 0),
            "downloads_last_month": recent.get("downloads_last_month", 0)
        }
    else:
        summary = {
            "package_name": pkg_name,
            "package_type": "pypi",
            "downloads_last_day": 0,
            "downloads_last_week": 0,
            "downloads_last_month": 0
        }

    pypi_summary_list.append(summary)

    # Get daily history
    daily = fetch_pypi_downloads_overall(pkg_name)
    if daily is not None and len(daily) > 0:
        pypi_daily_data[pkg_name] = daily

pypi_summary_df = pd.DataFrame(pypi_summary_list)

print(f"\n✓ Got data for {len([s for s in pypi_summary_list if s['downloads_last_week'] > 0])} packages")

# Show summary
print("\nPyPI packages by weekly downloads:")
display(pypi_summary_df.sort_values("downloads_last_week", ascending=False))

# Create time series DataFrame for charts
pypi_timeseries_list = []
for pkg_name, daily_df in pypi_daily_data.items():
    if len(daily_df) > 0:
        # Filter for "with_mirrors" category which has total downloads
        if "category" in daily_df.columns:
            daily_df = daily_df[daily_df["category"] == "with_mirrors"].copy()

        if len(daily_df) > 0:
            daily_df["package_name"] = pkg_name
            pypi_timeseries_list.append(daily_df)

if pypi_timeseries_list:
    pypi_timeseries_df = pd.concat(pypi_timeseries_list, ignore_index=True)
    if "date" in pypi_timeseries_df.columns:
        pypi_timeseries_df["date"] = pd.to_datetime(pypi_timeseries_df["date"])
    print(f"\n✓ Created PyPI time series with {len(pypi_timeseries_df)} records")
else:
    pypi_timeseries_df = pd.DataFrame(columns=["date", "downloads", "package_name"])
