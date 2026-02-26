# Cell 12: Page 1 Visualizations - Ecosystem Overview
# KPI cards, growth trends, top servers, category distribution

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Color palette (professional blue/teal theme)
COLORS = {
    "primary": "#2563eb",      # Blue
    "secondary": "#0891b2",    # Teal
    "accent": "#7c3aed",       # Purple
    "success": "#059669",      # Green
    "warning": "#d97706",      # Orange
    "neutral": "#6b7280",      # Gray
    "background": "#f8fafc"
}

CHART_TEMPLATE = "plotly_white"

# ============================================
# KPI CARDS (use Hex's metric component)
# ============================================

# These values will be displayed as Hex metric cards
kpi_total_servers = ecosystem_kpis["total_servers"]
kpi_weekly_downloads = ecosystem_kpis["total_downloads_weekly"]
kpi_total_stars = ecosystem_kpis["total_github_stars"]
kpi_active_pct = ecosystem_kpis["active_percentage"]

print("📊 KPI Card Values for Hex Metric Components:")
print(f"   Total MCP Servers: {kpi_total_servers}")
print(f"   Weekly Downloads: {kpi_weekly_downloads:,}")
print(f"   Total GitHub Stars: {kpi_total_stars:,}")
print(f"   Active Servers: {kpi_active_pct}%")

# ============================================
# TOP 10 SERVERS BY STARS (Bar Chart)
# ============================================

top_servers_stars = servers_enriched_df.nlargest(10, "github_stars")[
    ["name", "github_stars", "author"]
].copy()

fig_top_stars = px.bar(
    top_servers_stars,
    x="github_stars",
    y="name",
    orientation="h",
    title="Top 10 MCP Servers by GitHub Stars",
    labels={"github_stars": "Stars", "name": "Server"},
    color="github_stars",
    color_continuous_scale="Blues",
    text="github_stars"
)

fig_top_stars.update_traces(textposition="outside")
fig_top_stars.update_layout(
    template=CHART_TEMPLATE,
    showlegend=False,
    yaxis={"categoryorder": "total ascending"},
    height=400,
    coloraxis_showscale=False
)

fig_top_stars.show()

# ============================================
# TOP 10 SERVERS BY DOWNLOADS (Bar Chart)
# ============================================

top_servers_downloads = servers_enriched_df[
    servers_enriched_df["total_downloads_week"] > 0
].nlargest(10, "total_downloads_week")[
    ["name", "total_downloads_week", "npm_downloads_week", "pypi_downloads_week"]
].copy()

if len(top_servers_downloads) > 0:
    fig_top_downloads = px.bar(
        top_servers_downloads,
        x="total_downloads_week",
        y="name",
        orientation="h",
        title="Top 10 MCP Servers by Weekly Downloads",
        labels={"total_downloads_week": "Downloads/Week", "name": "Server"},
        color="total_downloads_week",
        color_continuous_scale="Teal",
        text="total_downloads_week"
    )

    fig_top_downloads.update_traces(textposition="outside")
    fig_top_downloads.update_layout(
        template=CHART_TEMPLATE,
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        height=400,
        coloraxis_showscale=False
    )

    fig_top_downloads.show()

# ============================================
# CATEGORY DISTRIBUTION (Pie/Donut Chart)
# ============================================

category_df = pd.DataFrame([
    {"category": cat, "count": count}
    for cat, count in category_counts.items()
]).head(10)

if len(category_df) > 0:
    fig_categories = px.pie(
        category_df,
        values="count",
        names="category",
        title="MCP Server Categories",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_categories.update_layout(
        template=CHART_TEMPLATE,
        height=400
    )

    fig_categories.show()

# ============================================
# ECOSYSTEM DISTRIBUTION (npm vs PyPI)
# ============================================

ecosystem_df = pd.DataFrame([
    {"ecosystem": eco, "count": count}
    for eco, count in ecosystem_distribution.items()
])

fig_ecosystem = px.pie(
    ecosystem_df,
    values="count",
    names="ecosystem",
    title="Server Ecosystem Distribution",
    hole=0.4,
    color_discrete_map={
        "TypeScript/JavaScript": COLORS["primary"],
        "Python": COLORS["warning"],
        "Unknown": COLORS["neutral"]
    }
)

fig_ecosystem.update_layout(
    template=CHART_TEMPLATE,
    height=350
)

fig_ecosystem.show()

# ============================================
# ACTIVITY LEVEL DISTRIBUTION (Bar Chart)
# ============================================

activity_df = pd.DataFrame([
    {"level": level, "count": count}
    for level, count in activity_distribution.items()
])

activity_order = ["Active", "Recent", "Moderate", "Stale", "Unknown"]
activity_df["level"] = pd.Categorical(activity_df["level"], categories=activity_order, ordered=True)
activity_df = activity_df.sort_values("level")

activity_colors = {
    "Active": COLORS["success"],
    "Recent": COLORS["primary"],
    "Moderate": COLORS["warning"],
    "Stale": COLORS["neutral"],
    "Unknown": "#d1d5db"
}

fig_activity = px.bar(
    activity_df,
    x="level",
    y="count",
    title="Server Activity Levels",
    labels={"level": "Activity Level", "count": "Number of Servers"},
    color="level",
    color_discrete_map=activity_colors,
    text="count"
)

fig_activity.update_traces(textposition="outside")
fig_activity.update_layout(
    template=CHART_TEMPLATE,
    showlegend=False,
    height=350
)

fig_activity.show()
