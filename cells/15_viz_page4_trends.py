# Cell 15: Page 4 - Trends & Velocity
# SDK trends, ecosystem growth, language split, company leaderboard

# ============================================
# OFFICIAL SDK DOWNLOAD TRENDS
# ============================================

print("📈 Official SDK Download Trends")

# npm SDK trend
sdk_npm_name = "@modelcontextprotocol/sdk"
if sdk_npm_name in npm_daily:
    sdk_npm_ts = npm_daily[sdk_npm_name].copy()
    sdk_npm_ts["day"] = pd.to_datetime(sdk_npm_ts["day"])
    sdk_npm_ts["sdk"] = "npm (@modelcontextprotocol/sdk)"

    # Calculate 7-day rolling average
    sdk_npm_ts["downloads_7d_avg"] = sdk_npm_ts["downloads"].rolling(7).mean()

# PyPI SDK trend
sdk_pypi_name = "mcp"
pypi_sdk_ts = None
if sdk_pypi_name in pypi_daily_data:
    pypi_sdk_ts = pypi_daily_data[sdk_pypi_name].copy()
    if "category" in pypi_sdk_ts.columns:
        pypi_sdk_ts = pypi_sdk_ts[pypi_sdk_ts["category"] == "with_mirrors"]
    if "date" in pypi_sdk_ts.columns:
        pypi_sdk_ts["date"] = pd.to_datetime(pypi_sdk_ts["date"])
        pypi_sdk_ts["sdk"] = "PyPI (mcp)"
        pypi_sdk_ts = pypi_sdk_ts.rename(columns={"date": "day"})
        pypi_sdk_ts["downloads_7d_avg"] = pypi_sdk_ts["downloads"].rolling(7).mean()

# Combine SDK trends
sdk_trends = []
if sdk_npm_name in npm_daily:
    sdk_trends.append(sdk_npm_ts[["day", "downloads", "sdk", "downloads_7d_avg"]])
if pypi_sdk_ts is not None and len(pypi_sdk_ts) > 0:
    sdk_trends.append(pypi_sdk_ts[["day", "downloads", "sdk", "downloads_7d_avg"]])

if sdk_trends:
    combined_sdk = pd.concat(sdk_trends, ignore_index=True)

    fig_sdk_trend = px.line(
        combined_sdk,
        x="day",
        y="downloads_7d_avg",
        color="sdk",
        title="Official MCP SDK Downloads (7-day Rolling Average)",
        labels={"day": "Date", "downloads_7d_avg": "Daily Downloads (7d avg)", "sdk": "SDK"},
        color_discrete_map={
            "npm (@modelcontextprotocol/sdk)": COLORS["primary"],
            "PyPI (mcp)": COLORS["warning"]
        }
    )

    fig_sdk_trend.update_layout(
        template=CHART_TEMPLATE,
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig_sdk_trend.show()

# ============================================
# ECOSYSTEM npm vs PyPI COMPARISON
# ============================================

print("\n📊 Ecosystem Comparison: npm vs PyPI")

ecosystem_comparison = pd.DataFrame([
    {"Metric": "Total Servers", "npm": servers_with_npm, "PyPI": servers_with_pypi},
    {"Metric": "Weekly Downloads", "npm": int(total_npm_weekly), "PyPI": int(total_pypi_weekly)},
    {"Metric": "SDK Weekly Downloads", "npm": int(sdk_npm_downloads), "PyPI": int(sdk_pypi_downloads)}
])

display(ecosystem_comparison)

fig_ecosystem_compare = px.bar(
    ecosystem_comparison.melt(id_vars="Metric", var_name="Ecosystem", value_name="Value"),
    x="Metric",
    y="Value",
    color="Ecosystem",
    barmode="group",
    title="npm vs PyPI Ecosystem Comparison",
    color_discrete_map={"npm": COLORS["primary"], "PyPI": COLORS["warning"]}
)

fig_ecosystem_compare.update_layout(
    template=CHART_TEMPLATE,
    height=350
)

fig_ecosystem_compare.show()

# ============================================
# LANGUAGE DISTRIBUTION ACROSS SERVERS
# ============================================

print("\n🗣️ Programming Language Distribution")

if "github_language" in servers_enriched_df.columns:
    language_dist = servers_enriched_df["github_language"].value_counts().head(10).reset_index()
    language_dist.columns = ["Language", "Count"]

    fig_languages = px.bar(
        language_dist,
        x="Count",
        y="Language",
        orientation="h",
        title="MCP Servers by Programming Language",
        color="Count",
        color_continuous_scale="Viridis",
        text="Count"
    )

    fig_languages.update_traces(textposition="outside")
    fig_languages.update_layout(
        template=CHART_TEMPLATE,
        height=400,
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False
    )

    fig_languages.show()

# ============================================
# COMPANY LEADERBOARD
# ============================================

print("\n🏢 Company/Author Leaderboard")

# Group by author
author_stats = servers_enriched_df.groupby("author").agg({
    "name": "count",
    "github_stars": "sum",
    "total_downloads_week": "sum"
}).reset_index()

author_stats.columns = ["Author", "Server Count", "Total Stars", "Weekly Downloads"]
author_stats = author_stats.sort_values("Server Count", ascending=False).head(15)

# Filter out empty/unknown authors
author_stats = author_stats[author_stats["Author"].notna() & (author_stats["Author"] != "")]

display(author_stats.head(10))

fig_authors = px.bar(
    author_stats.head(10),
    x="Server Count",
    y="Author",
    orientation="h",
    title="Top Contributors to MCP Ecosystem (by Server Count)",
    color="Total Stars",
    color_continuous_scale="Blues",
    text="Server Count"
)

fig_authors.update_traces(textposition="outside")
fig_authors.update_layout(
    template=CHART_TEMPLATE,
    height=400,
    yaxis={"categoryorder": "total ascending"}
)

fig_authors.show()

# ============================================
# POPULARITY TIER OVER TIME (if historical data available)
# ============================================

# This would require historical snapshots - showing current distribution
print("\n📊 Current Popularity Tier Distribution")

tier_summary = servers_enriched_df["popularity_tier"].value_counts().reset_index()
tier_summary.columns = ["Tier", "Count"]

tier_order = ["Top Tier", "Popular", "Growing", "Emerging"]
tier_summary["Tier"] = pd.Categorical(tier_summary["Tier"], categories=tier_order, ordered=True)
tier_summary = tier_summary.sort_values("Tier")

fig_tiers = px.funnel(
    tier_summary,
    x="Count",
    y="Tier",
    title="MCP Server Popularity Distribution",
    color="Tier",
    color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["accent"], COLORS["neutral"]]
)

fig_tiers.update_layout(
    template=CHART_TEMPLATE,
    height=350
)

fig_tiers.show()

# ============================================
# RECENT ACTIVITY HEATMAP
# ============================================

print("\n🔥 Server Activity Summary")

# Create activity summary
activity_summary = pd.DataFrame({
    "Activity Level": ["Active (≤7 days)", "Recent (≤30 days)", "Moderate (≤90 days)", "Stale (>90 days)"],
    "Count": [
        activity_distribution.get("Active", 0),
        activity_distribution.get("Recent", 0),
        activity_distribution.get("Moderate", 0),
        activity_distribution.get("Stale", 0)
    ]
})

display(activity_summary)
