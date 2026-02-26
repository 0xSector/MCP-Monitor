# Cell 13: Page 2 - Server Discovery Table
# Interactive filterable/searchable table of all MCP servers

# ============================================
# PREPARE TABLE DATA
# ============================================

# Select and rename columns for the table
table_columns = {
    "name": "Name",
    "author": "Author/Company",
    "description": "Description",
    "github_stars": "Stars",
    "total_downloads_week": "Downloads/Week",
    "activity_level": "Activity",
    "popularity_tier": "Tier",
    "ecosystem": "Ecosystem",
    "categories": "Categories",
    "source": "Source",
    "repository": "Repository"
}

server_table_df = servers_enriched_df[[col for col in table_columns.keys() if col in servers_enriched_df.columns]].copy()
server_table_df = server_table_df.rename(columns=table_columns)

# Fill NaN values for display
server_table_df["Stars"] = server_table_df["Stars"].fillna(0).astype(int)
server_table_df["Downloads/Week"] = server_table_df["Downloads/Week"].fillna(0).astype(int)
server_table_df["Description"] = server_table_df["Description"].fillna("").str[:100]
server_table_df["Categories"] = server_table_df["Categories"].fillna("")

# Sort by stars by default
server_table_df = server_table_df.sort_values("Stars", ascending=False)

print(f"Server Discovery Table: {len(server_table_df)} servers")
print("Columns:", list(server_table_df.columns))

# ============================================
# HEX TABLE FILTERS (Input Components)
# ============================================

# These would be Hex input components - defining defaults here
# In Hex, use: hx.input_select(), hx.input_text()

# Filter: Activity Level
activity_filter_options = ["All"] + list(servers_enriched_df["activity_level"].unique())
selected_activity = "All"  # Hex input component

# Filter: Popularity Tier
tier_filter_options = ["All"] + list(servers_enriched_df["popularity_tier"].unique())
selected_tier = "All"  # Hex input component

# Filter: Ecosystem
ecosystem_filter_options = ["All"] + list(servers_enriched_df["ecosystem"].unique())
selected_ecosystem = "All"  # Hex input component

# Filter: Source
source_filter_options = ["All"] + list(servers_enriched_df["source"].unique())
selected_source = "All"  # Hex input component

# Search text
search_text = ""  # Hex text input component

print("\n📋 Available Filters:")
print(f"   Activity Levels: {activity_filter_options}")
print(f"   Popularity Tiers: {tier_filter_options}")
print(f"   Ecosystems: {ecosystem_filter_options}")
print(f"   Sources: {source_filter_options}")

# ============================================
# APPLY FILTERS (Reactive in Hex)
# ============================================

filtered_table_df = server_table_df.copy()

# Apply activity filter
if selected_activity != "All":
    filtered_table_df = filtered_table_df[filtered_table_df["Activity"] == selected_activity]

# Apply tier filter
if selected_tier != "All":
    filtered_table_df = filtered_table_df[filtered_table_df["Tier"] == selected_tier]

# Apply ecosystem filter
if selected_ecosystem != "All":
    filtered_table_df = filtered_table_df[filtered_table_df["Ecosystem"] == selected_ecosystem]

# Apply source filter
if selected_source != "All":
    filtered_table_df = filtered_table_df[filtered_table_df["Source"] == selected_source]

# Apply search filter
if search_text:
    search_lower = search_text.lower()
    filtered_table_df = filtered_table_df[
        filtered_table_df["Name"].str.lower().str.contains(search_lower, na=False) |
        filtered_table_df["Description"].str.lower().str.contains(search_lower, na=False) |
        filtered_table_df["Author/Company"].str.lower().str.contains(search_lower, na=False) |
        filtered_table_df["Categories"].str.lower().str.contains(search_lower, na=False)
    ]

print(f"\nFiltered Results: {len(filtered_table_df)} servers")

# ============================================
# DISPLAY TABLE
# ============================================

# In Hex, this would be displayed as an interactive data table
# with sorting, filtering, and click-through capabilities

display(filtered_table_df)

# ============================================
# SUMMARY STATS FOR FILTERED DATA
# ============================================

print("\n📊 Filtered Data Summary:")
print(f"   Total Servers: {len(filtered_table_df)}")
print(f"   Total Stars: {filtered_table_df['Stars'].sum():,}")
print(f"   Total Downloads/Week: {filtered_table_df['Downloads/Week'].sum():,}")
print(f"   Avg Stars: {filtered_table_df['Stars'].mean():.1f}")

# Export-ready dataframe
server_table_export = filtered_table_df.copy()
