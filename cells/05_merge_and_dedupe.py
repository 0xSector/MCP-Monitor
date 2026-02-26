# Cell 5: Merge and Deduplicate Servers
# Combines all discovery sources into a unified server list

def normalize_repo_url(url: str) -> str:
    """Normalize GitHub URLs for comparison."""
    if not url:
        return ""
    url = url.lower().strip()
    url = url.replace("https://", "").replace("http://", "")
    url = url.replace("www.", "")
    url = url.rstrip("/")
    url = url.replace(".git", "")
    return url

def merge_server_records(records: List[Dict]) -> Dict:
    """Merge multiple records for the same server, preferring non-null values."""
    if len(records) == 1:
        return records[0]

    merged = {}
    # Priority order: curated > mcp_registry > github_search
    priority_order = {"curated": 0, "mcp_registry": 1, "github_search": 2}
    records_sorted = sorted(records, key=lambda x: priority_order.get(x.get("source", ""), 99))

    for key in records[0].keys():
        for rec in records_sorted:
            val = rec.get(key)
            if val is not None and val != "" and str(val) != "nan":
                merged[key] = val
                break
        if key not in merged:
            merged[key] = None

    # Combine sources
    sources = list(set(r.get("source", "") for r in records if r.get("source")))
    merged["sources"] = ",".join(sources)

    return merged

# Prepare DataFrames with common columns
common_cols = [
    "server_id", "name", "description", "repository",
    "npm_package", "pypi_package", "categories", "author",
    "version", "source", "discovered_date"
]

# Ensure all dataframes have required columns
def ensure_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for col in cols:
        if col not in df.columns:
            df[col] = None
    return df[cols]

print("Merging server sources...")

# Combine all sources
all_sources = []

if 'registry_servers_df' in dir() and len(registry_servers_df) > 0:
    registry_norm = ensure_columns(registry_servers_df.copy(), common_cols)
    all_sources.append(registry_norm)
    print(f"  MCP Registry: {len(registry_norm)} servers")

if 'github_discovered_df' in dir() and len(github_discovered_df) > 0:
    github_norm = ensure_columns(github_discovered_df.copy(), common_cols)
    all_sources.append(github_norm)
    print(f"  GitHub Search: {len(github_norm)} servers")

if 'curated_servers_df' in dir() and len(curated_servers_df) > 0:
    curated_norm = ensure_columns(curated_servers_df.copy(), common_cols)
    all_sources.append(curated_norm)
    print(f"  Curated List: {len(curated_norm)} servers")

if not all_sources:
    raise ValueError("No server data available from any source")

# Concatenate all sources
combined_df = pd.concat(all_sources, ignore_index=True)
print(f"\nTotal before deduplication: {len(combined_df)}")

# Add normalized repo URL for deduplication
combined_df["repo_normalized"] = combined_df["repository"].apply(normalize_repo_url)

# Group by normalized repo URL and merge
deduped_records = []
repo_groups = combined_df.groupby("repo_normalized")

for repo_url, group in repo_groups:
    if not repo_url:  # Skip empty repos
        # Keep all records without repo URLs
        for _, row in group.iterrows():
            deduped_records.append(row.to_dict())
    else:
        # Merge records with same repo
        records = group.to_dict("records")
        merged = merge_server_records(records)
        deduped_records.append(merged)

# Create deduplicated DataFrame
servers_master_df = pd.DataFrame(deduped_records)

# Generate unique server_id if missing
servers_master_df["server_id"] = servers_master_df.apply(
    lambda x: x["server_id"] if pd.notna(x["server_id"]) and x["server_id"]
    else x["name"].lower().replace(" ", "_")[:50] if pd.notna(x["name"])
    else f"server_{hash(str(x['repository']))}"[:20],
    axis=1
)

# Clean up
if "repo_normalized" in servers_master_df.columns:
    servers_master_df = servers_master_df.drop(columns=["repo_normalized"])

print(f"✓ After deduplication: {len(servers_master_df)} unique servers")

# Summary by source
if "sources" in servers_master_df.columns:
    print("\nServers by source combination:")
    print(servers_master_df["sources"].value_counts().head(10))
else:
    print("\nServers by source:")
    print(servers_master_df["source"].value_counts())

display(servers_master_df.head(10))
