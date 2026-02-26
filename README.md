# MCP Ecosystem Adoption Dashboard

An interactive Hex dashboard tracking the entire MCP (Model Context Protocol) server ecosystem.

## Quick Start

### Option 1: Single File Import
1. Open Hex and create a new project
2. Copy contents of `mcp_dashboard_complete.py` into a Python cell
3. Split into separate cells at each `# Cell X:` comment
4. Run all cells

### Option 2: Cell-by-Cell Import
Import individual cells from the `cells/` directory in order:
1. `01_config_and_imports.py` - Configuration
2. `02_fetch_mcp_registry.py` - Registry API
3. `03_github_discovery.py` - GitHub search
4. `04_curated_servers.py` - Manual server list
5. `05_merge_and_dedupe.py` - Deduplication
6. `06_github_metrics.py` - GitHub metrics
7. `07_npm_downloads.py` - npm downloads
8. `08_pypi_downloads.py` - PyPI downloads
9. `09_join_all_data.py` - Data joining
10. `10_derived_metrics.py` - Health scores
11. `11_ecosystem_kpis.py` - KPI calculations
12. `12_viz_page1_overview.py` - Overview page
13. `13_viz_page2_server_table.py` - Server table
14. `14_viz_page3_server_deepdive.py` - Deep dive
15. `15_viz_page4_trends.py` - Trends page
16. `16_automation_refresh.py` - Automation

## Dashboard Pages

### Page 1: Ecosystem Overview
- KPI cards: Total servers, weekly downloads, GitHub stars
- Top 10 servers by stars (bar chart)
- Category distribution (donut chart)
- Activity level breakdown

### Page 2: Server Discovery Table
- Searchable/filterable table of all MCP servers
- Filters: Activity, Popularity Tier, Ecosystem, Source
- Columns: Name, Author, Stars, Downloads, Activity, Categories

### Page 3: Server Deep Dive
- Select any server for detailed view
- Download trend charts (npm/PyPI)
- Health score gauge
- Similar servers by category

### Page 4: Trends & Velocity
- Official SDK download trends
- npm vs PyPI ecosystem comparison
- Language distribution
- Company/author leaderboard

## Configuration

### GitHub Token (Recommended)
To avoid rate limits (60 req/hr → 5000 req/hr):

1. Create token at GitHub → Settings → Developer settings → Personal access tokens
2. Add to Hex Secrets: `GITHUB_TOKEN`
3. Uncomment in Cell 1: `GITHUB_TOKEN = hex_secrets.get("GITHUB_TOKEN", None)`

### Scheduled Refresh
1. Click Schedule in Hex
2. Set frequency: Weekly (full) or Daily (downloads only)
3. Enable failure notifications

## Data Sources

| Source | Endpoint | Purpose |
|--------|----------|---------|
| MCP Registry | `registry.modelcontextprotocol.io/v0` | Official server list |
| GitHub API | `api.github.com` | Repo metrics, discovery |
| npm API | `api.npmjs.org` | Package downloads |
| pypistats | `pypistats.org/api` | Python package stats |

## File Structure

```
mcp_ecosystem_dashboard/
├── README.md                    # This file
├── mcp_dashboard_complete.py    # Single-file version
└── cells/                       # Individual cells
    ├── 01_config_and_imports.py
    ├── 02_fetch_mcp_registry.py
    ├── ...
    └── 16_automation_refresh.py
```

## Adding Custom Servers

Edit the `CURATED_SERVERS` list in Cell 4 or use Hex Input Tables:

```python
{
    "name": "My MCP Server",
    "repository": "https://github.com/org/repo",
    "npm_package": "@org/mcp-server",  # or None
    "pypi_package": "mcp-server",       # or None
    "company": "Company Name",
    "category": "category1,category2"
}
```

## Output Tables

| Table | Description |
|-------|-------------|
| `servers_enriched_df` | All servers with metrics |
| `ecosystem_kpis_df` | Aggregate KPIs |
| `npm_timeseries_df` | Daily npm downloads |
| `pypi_timeseries_df` | Daily PyPI downloads |

## Rate Limits

- **GitHub**: 60/hr (unauth) or 5000/hr (with token)
- **npm**: ~100/hr
- **pypistats**: ~100/hr

Full refresh with 100+ servers takes approximately:
- Without GitHub token: 30-60 minutes
- With GitHub token: 5-10 minutes
