# Cell 14: Page 3 - Server Deep Dive (Parameterized)
# Detailed view of a single selected server

# ============================================
# SERVER SELECTOR (Hex Input Component)
# ============================================

# In Hex, use: hx.input_select(options=server_names, value=default)
server_names = servers_enriched_df["name"].dropna().tolist()
selected_server = server_names[0] if server_names else None  # Default to first server

print(f"Available servers for deep dive: {len(server_names)}")
print(f"Selected server: {selected_server}")

# ============================================
# GET SELECTED SERVER DATA
# ============================================

if selected_server:
    server_data = servers_enriched_df[servers_enriched_df["name"] == selected_server].iloc[0]

    print("\n" + "="*60)
    print(f"📦 {selected_server}")
    print("="*60)

    # Basic Info
    print(f"\n📝 Description: {server_data.get('description', 'N/A')[:200]}")
    print(f"👤 Author: {server_data.get('author', 'Unknown')}")
    print(f"🔗 Repository: {server_data.get('repository', 'N/A')}")

    # Packages
    npm_pkg = server_data.get('npm_package')
    pypi_pkg = server_data.get('pypi_package')
    print(f"\n📦 npm Package: {npm_pkg if pd.notna(npm_pkg) else 'N/A'}")
    print(f"🐍 PyPI Package: {pypi_pkg if pd.notna(pypi_pkg) else 'N/A'}")

    # Metrics
    print(f"\n📊 METRICS")
    print(f"   Health Score: {server_data.get('health_score', 0):.0f}/100")
    print(f"   Activity: {server_data.get('activity_level', 'Unknown')}")
    print(f"   Tier: {server_data.get('popularity_tier', 'Unknown')}")

    print(f"\n⭐ GitHub Stats")
    print(f"   Stars: {int(server_data.get('github_stars', 0) or 0):,}")
    print(f"   Forks: {int(server_data.get('github_forks', 0) or 0):,}")
    print(f"   Open Issues: {int(server_data.get('github_open_issues', 0) or 0)}")
    print(f"   Language: {server_data.get('github_language', 'Unknown')}")

    print(f"\n📥 Downloads (Weekly)")
    print(f"   npm: {int(server_data.get('npm_downloads_week', 0) or 0):,}")
    print(f"   PyPI: {int(server_data.get('pypi_downloads_week', 0) or 0):,}")
    print(f"   Total: {int(server_data.get('total_downloads_week', 0) or 0):,}")

    # ============================================
    # DOWNLOAD TREND CHART
    # ============================================

    # Get npm time series for selected server
    npm_pkg = server_data.get('npm_package')
    if npm_pkg and npm_pkg in npm_daily:
        npm_ts = npm_daily[npm_pkg].copy()
        npm_ts["day"] = pd.to_datetime(npm_ts["day"])
        npm_ts["source"] = "npm"
        npm_ts = npm_ts.rename(columns={"day": "date"})

        fig_downloads = px.line(
            npm_ts,
            x="date",
            y="downloads",
            title=f"npm Downloads Trend: {npm_pkg}",
            labels={"date": "Date", "downloads": "Daily Downloads"},
            color_discrete_sequence=[COLORS["primary"]]
        )

        fig_downloads.update_layout(
            template=CHART_TEMPLATE,
            height=350
        )

        fig_downloads.show()

    # Get PyPI time series for selected server
    pypi_pkg = server_data.get('pypi_package')
    if pypi_pkg and pypi_pkg in pypi_daily_data:
        pypi_ts = pypi_daily_data[pypi_pkg].copy()
        if "date" in pypi_ts.columns:
            pypi_ts["date"] = pd.to_datetime(pypi_ts["date"])

            if "category" in pypi_ts.columns:
                pypi_ts = pypi_ts[pypi_ts["category"] == "with_mirrors"]

            fig_pypi = px.line(
                pypi_ts,
                x="date",
                y="downloads",
                title=f"PyPI Downloads Trend: {pypi_pkg}",
                labels={"date": "Date", "downloads": "Daily Downloads"},
                color_discrete_sequence=[COLORS["warning"]]
            )

            fig_pypi.update_layout(
                template=CHART_TEMPLATE,
                height=350
            )

            fig_pypi.show()

    # ============================================
    # HEALTH SCORE GAUGE
    # ============================================

    health_score = server_data.get('health_score', 0)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        title={"text": "Health Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS["primary"]},
            "steps": [
                {"range": [0, 33], "color": "#fee2e2"},
                {"range": [33, 66], "color": "#fef3c7"},
                {"range": [66, 100], "color": "#d1fae5"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": health_score
            }
        }
    ))

    fig_gauge.update_layout(height=300)
    fig_gauge.show()

    # ============================================
    # SIMILAR SERVERS
    # ============================================

    # Find servers in same category
    server_categories = str(server_data.get('categories', '')).split(',')
    if server_categories and server_categories[0]:
        main_category = server_categories[0].strip()
        similar = servers_enriched_df[
            (servers_enriched_df["categories"].str.contains(main_category, na=False)) &
            (servers_enriched_df["name"] != selected_server)
        ].nlargest(5, "github_stars")[["name", "github_stars", "total_downloads_week"]]

        if len(similar) > 0:
            print(f"\n🔗 Similar Servers (Category: {main_category})")
            display(similar)
