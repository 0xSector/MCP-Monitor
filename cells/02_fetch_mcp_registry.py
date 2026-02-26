# Cell 2: Fetch MCP Registry Servers
# Fetches all registered MCP servers from the official registry with pagination

def fetch_mcp_registry_servers(limit_per_page: int = 100, max_pages: int = 50) -> pd.DataFrame:
    """
    Fetch all servers from MCP Registry with pagination.

    Returns DataFrame with columns:
    - server_id, name, description, repository, npm_package, pypi_package,
    - categories, author, version, created_at
    """
    all_servers = []
    cursor = None
    page = 0

    while page < max_pages:
        params = {"limit": limit_per_page}
        if cursor:
            params["cursor"] = cursor

        url = f"{MCP_REGISTRY_BASE}/servers"
        response = safe_request(url, params=params)

        if not response:
            print(f"Failed to fetch page {page + 1}")
            break

        servers = response.get("servers", response.get("items", []))
        if not servers:
            break

        for server in servers:
            # Extract package references
            package_info = server.get("package", {})
            npm_pkg = None
            pypi_pkg = None

            if isinstance(package_info, dict):
                npm_pkg = package_info.get("npm")
                pypi_pkg = package_info.get("pypi")
            elif isinstance(package_info, str):
                if "npmjs" in package_info or package_info.startswith("@"):
                    npm_pkg = package_info
                elif "pypi" in package_info:
                    pypi_pkg = package_info

            # Extract repository URL
            repo = server.get("repository", server.get("repo", server.get("source_url", "")))
            if isinstance(repo, dict):
                repo = repo.get("url", "")

            all_servers.append({
                "server_id": server.get("id", server.get("name", "")),
                "name": server.get("name", server.get("display_name", "")),
                "description": server.get("description", "")[:500] if server.get("description") else "",
                "repository": repo,
                "npm_package": npm_pkg,
                "pypi_package": pypi_pkg,
                "categories": ",".join(server.get("categories", [])) if isinstance(server.get("categories"), list) else server.get("categories", ""),
                "author": server.get("author", server.get("publisher", "")),
                "version": server.get("version", ""),
                "source": "mcp_registry",
                "discovered_date": datetime.now().strftime("%Y-%m-%d")
            })

        # Check for pagination cursor
        cursor = response.get("next_cursor", response.get("cursor"))
        if not cursor:
            break

        page += 1
        print(f"  Fetched page {page}, total servers: {len(all_servers)}")

    return pd.DataFrame(all_servers)

# Execute the fetch
print("Fetching MCP Registry servers...")
registry_servers_df = fetch_mcp_registry_servers()
print(f"✓ Found {len(registry_servers_df)} servers in MCP Registry")

# Display sample
if len(registry_servers_df) > 0:
    print("\nSample of registered servers:")
    display(registry_servers_df[["name", "description", "repository"]].head(10))
