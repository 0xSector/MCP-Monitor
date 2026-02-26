# Cell 10: Calculate Derived Metrics
# Computes health scores, growth rates, and categorizations

def calculate_health_score(row: pd.Series) -> float:
    """
    Calculate a composite health score (0-100) based on:
    - Activity: Recent commits, last updated
    - Popularity: Stars, downloads
    - Community: Issues activity, contributors
    """
    score = 0
    max_score = 100

    # Activity score (0-30 points)
    activity_score = 0
    if pd.notna(row.get("commits_last_4_weeks")) and row["commits_last_4_weeks"] > 0:
        activity_score += min(15, row["commits_last_4_weeks"])  # Up to 15 points for commits

    if pd.notna(row.get("github_pushed_at")):
        try:
            pushed = pd.to_datetime(row["github_pushed_at"])
            days_since_push = (datetime.now(pushed.tzinfo) - pushed).days
            if days_since_push <= 7:
                activity_score += 15
            elif days_since_push <= 30:
                activity_score += 10
            elif days_since_push <= 90:
                activity_score += 5
        except:
            pass

    score += min(30, activity_score)

    # Popularity score (0-40 points)
    popularity_score = 0
    if pd.notna(row.get("github_stars")):
        stars = row["github_stars"]
        if stars >= 1000:
            popularity_score += 20
        elif stars >= 100:
            popularity_score += 15
        elif stars >= 10:
            popularity_score += 10
        elif stars >= 1:
            popularity_score += 5

    downloads = row.get("total_downloads_week", 0) or 0
    if downloads >= 10000:
        popularity_score += 20
    elif downloads >= 1000:
        popularity_score += 15
    elif downloads >= 100:
        popularity_score += 10
    elif downloads >= 10:
        popularity_score += 5

    score += min(40, popularity_score)

    # Community score (0-30 points)
    community_score = 0
    if pd.notna(row.get("github_open_issues")) and row["github_open_issues"] > 0:
        # Having issues shows usage
        community_score += min(10, row["github_open_issues"])

    if pd.notna(row.get("github_forks")) and row["github_forks"] > 0:
        community_score += min(10, row["github_forks"] / 5)

    if pd.notna(row.get("github_contributors")) and row["github_contributors"] > 1:
        community_score += min(10, row["github_contributors"])

    score += min(30, community_score)

    return min(max_score, score)

def categorize_activity_level(row: pd.Series) -> str:
    """Categorize server activity level."""
    if pd.notna(row.get("github_pushed_at")):
        try:
            pushed = pd.to_datetime(row["github_pushed_at"])
            days_since = (datetime.now(pushed.tzinfo) - pushed).days

            if days_since <= 7:
                return "Active"
            elif days_since <= 30:
                return "Recent"
            elif days_since <= 90:
                return "Moderate"
            else:
                return "Stale"
        except:
            pass
    return "Unknown"

def categorize_popularity_tier(row: pd.Series) -> str:
    """Categorize server by popularity tier."""
    stars = row.get("github_stars", 0) or 0
    downloads = row.get("total_downloads_week", 0) or 0

    if stars >= 1000 or downloads >= 10000:
        return "Top Tier"
    elif stars >= 100 or downloads >= 1000:
        return "Popular"
    elif stars >= 10 or downloads >= 100:
        return "Growing"
    else:
        return "Emerging"

# Apply derived metrics
print("Calculating derived metrics...")

servers_enriched_df["health_score"] = servers_enriched_df.apply(calculate_health_score, axis=1)
servers_enriched_df["activity_level"] = servers_enriched_df.apply(categorize_activity_level, axis=1)
servers_enriched_df["popularity_tier"] = servers_enriched_df.apply(categorize_popularity_tier, axis=1)

# Calculate days since creation
if "github_created_at" in servers_enriched_df.columns:
    servers_enriched_df["days_since_creation"] = servers_enriched_df["github_created_at"].apply(
        lambda x: (datetime.now() - pd.to_datetime(x).replace(tzinfo=None)).days
        if pd.notna(x) else None
    )

# Determine primary language/ecosystem
servers_enriched_df["ecosystem"] = servers_enriched_df.apply(
    lambda x: "TypeScript/JavaScript" if pd.notna(x.get("npm_package"))
    else "Python" if pd.notna(x.get("pypi_package"))
    else x.get("github_language", "Unknown"),
    axis=1
)

print("✓ Derived metrics calculated")

# Show distribution
print("\nActivity Level Distribution:")
print(servers_enriched_df["activity_level"].value_counts())

print("\nPopularity Tier Distribution:")
print(servers_enriched_df["popularity_tier"].value_counts())

print("\nEcosystem Distribution:")
print(servers_enriched_df["ecosystem"].value_counts())

# Show top servers by health score
print("\nTop 10 Servers by Health Score:")
display(servers_enriched_df.nlargest(10, "health_score")[[
    "name", "health_score", "activity_level", "popularity_tier", "github_stars", "total_downloads_week"
]])
