# Cell 6: Fetch GitHub Repository Metrics
# Enriches servers with detailed GitHub metrics

def extract_github_owner_repo(url: str) -> tuple:
    """Extract owner and repo name from GitHub URL."""
    if not url or "github.com" not in url:
        return None, None

    # Clean URL
    url = url.replace("https://", "").replace("http://", "")
    url = url.replace("www.", "").replace("github.com/", "")
    url = url.rstrip("/").replace(".git", "")

    parts = url.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None

def fetch_github_repo_metrics(owner: str, repo: str) -> Optional[Dict]:
    """Fetch detailed metrics for a GitHub repository."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    data = safe_request(url, delay=GITHUB_RATE_LIMIT_DELAY)

    if not data:
        return None

    return {
        "github_stars": data.get("stargazers_count", 0),
        "github_forks": data.get("forks_count", 0),
        "github_watchers": data.get("watchers_count", 0),
        "github_open_issues": data.get("open_issues_count", 0),
        "github_size_kb": data.get("size", 0),
        "github_language": data.get("language", ""),
        "github_license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
        "github_default_branch": data.get("default_branch", "main"),
        "github_created_at": data.get("created_at", ""),
        "github_updated_at": data.get("updated_at", ""),
        "github_pushed_at": data.get("pushed_at", ""),
        "github_archived": data.get("archived", False),
        "github_disabled": data.get("disabled", False),
        "github_topics": ",".join(data.get("topics", []))
    }

def fetch_github_commit_activity(owner: str, repo: str) -> Dict:
    """Fetch recent commit activity."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/stats/commit_activity"
    data = safe_request(url, delay=GITHUB_RATE_LIMIT_DELAY)

    if not data or not isinstance(data, list):
        return {"commits_last_week": 0, "commits_last_4_weeks": 0}

    # Sum commits from last 4 weeks
    recent_weeks = data[-4:] if len(data) >= 4 else data
    commits_4w = sum(week.get("total", 0) for week in recent_weeks)
    commits_1w = data[-1].get("total", 0) if data else 0

    return {
        "commits_last_week": commits_1w,
        "commits_last_4_weeks": commits_4w
    }

def fetch_github_contributors_count(owner: str, repo: str) -> int:
    """Fetch contributor count (first page only for efficiency)."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contributors"
    params = {"per_page": 1, "anon": "false"}
    headers = {}

    try:
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"

        response = requests.get(url, headers=headers, params=params, timeout=30)
        time.sleep(GITHUB_RATE_LIMIT_DELAY)

        # Get count from Link header
        link_header = response.headers.get("Link", "")
        if 'rel="last"' in link_header:
            # Parse last page number
            import re
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                return int(match.group(1))
        return len(response.json()) if response.ok else 0
    except:
        return 0

# Enrich servers with GitHub metrics
print("Fetching GitHub metrics for servers...")
print(f"Processing {len(servers_master_df)} servers (this may take a while due to rate limits)...")

github_metrics_list = []

for idx, row in servers_master_df.iterrows():
    repo_url = row.get("repository", "")
    owner, repo = extract_github_owner_repo(repo_url)

    if not owner or not repo:
        github_metrics_list.append({
            "server_id": row["server_id"],
            "has_github": False
        })
        continue

    print(f"  [{idx+1}/{len(servers_master_df)}] Fetching: {owner}/{repo}")

    # Fetch basic metrics
    metrics = fetch_github_repo_metrics(owner, repo)

    if not metrics:
        github_metrics_list.append({
            "server_id": row["server_id"],
            "has_github": False
        })
        continue

    # Add commit activity
    commit_stats = fetch_github_commit_activity(owner, repo)
    metrics.update(commit_stats)

    # Add contributor count (expensive, sample for large datasets)
    if len(servers_master_df) <= 50:  # Only fetch for small datasets
        metrics["github_contributors"] = fetch_github_contributors_count(owner, repo)

    metrics["server_id"] = row["server_id"]
    metrics["has_github"] = True
    metrics["github_owner"] = owner
    metrics["github_repo"] = repo

    github_metrics_list.append(metrics)

github_metrics_df = pd.DataFrame(github_metrics_list)
print(f"\n✓ Fetched GitHub metrics for {github_metrics_df['has_github'].sum()} repositories")

# Show top by stars
if "github_stars" in github_metrics_df.columns:
    top_stars = github_metrics_df[github_metrics_df["has_github"] == True].nlargest(10, "github_stars")
    print("\nTop 10 by GitHub stars:")
    display(top_stars[["server_id", "github_stars", "github_forks", "github_language"]].head(10))
