# Cell 3: GitHub Discovery - Find MCP Repos via Search
# Discovers MCP servers through GitHub Search API queries

def github_search_repos(query: str, max_results: int = 100) -> List[Dict]:
    """Search GitHub repos with pagination."""
    repos = []
    per_page = min(100, max_results)
    pages_needed = (max_results + per_page - 1) // per_page

    for page in range(1, pages_needed + 1):
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }

        response = safe_request(
            f"{GITHUB_API_BASE}/search/repositories",
            params=params,
            delay=GITHUB_RATE_LIMIT_DELAY
        )

        if not response or "items" not in response:
            break

        repos.extend(response["items"])

        if len(response["items"]) < per_page:
            break

    return repos[:max_results]

def extract_package_refs(repo: Dict) -> tuple:
    """Try to infer npm/PyPI package names from repo metadata."""
    npm_pkg = None
    pypi_pkg = None
    name = repo.get("name", "").lower()
    full_name = repo.get("full_name", "")

    # Check topics for hints
    topics = repo.get("topics", [])

    # Check language to guess package type
    language = repo.get("language", "").lower()

    if language in ["typescript", "javascript"]:
        # Likely npm package - use repo name as guess
        if "mcp" in name:
            npm_pkg = name
    elif language == "python":
        # Likely PyPI package
        if "mcp" in name:
            pypi_pkg = name.replace("-", "_")

    return npm_pkg, pypi_pkg

# Define search queries for MCP discovery
SEARCH_QUERIES = [
    "topic:mcp",
    "topic:model-context-protocol",
    '"mcp server" in:readme',
    "mcp-server in:name",
    '"@modelcontextprotocol" in:readme',
    "model-context-protocol in:name"
]

# Execute searches
print("Searching GitHub for MCP repositories...")
all_github_repos = []
seen_repo_ids = set()

for query in SEARCH_QUERIES:
    print(f"  Searching: {query}")
    repos = github_search_repos(query, max_results=100)

    for repo in repos:
        repo_id = repo.get("id")
        if repo_id not in seen_repo_ids:
            seen_repo_ids.add(repo_id)

            npm_pkg, pypi_pkg = extract_package_refs(repo)

            all_github_repos.append({
                "server_id": f"github_{repo_id}",
                "name": repo.get("name", ""),
                "description": (repo.get("description", "") or "")[:500],
                "repository": repo.get("html_url", ""),
                "npm_package": npm_pkg,
                "pypi_package": pypi_pkg,
                "categories": ",".join(repo.get("topics", [])),
                "author": repo.get("owner", {}).get("login", ""),
                "version": "",
                "source": "github_search",
                "discovered_date": datetime.now().strftime("%Y-%m-%d"),
                # Extra GitHub metadata
                "github_stars": repo.get("stargazers_count", 0),
                "github_forks": repo.get("forks_count", 0),
                "github_open_issues": repo.get("open_issues_count", 0),
                "github_language": repo.get("language", ""),
                "github_updated_at": repo.get("updated_at", ""),
                "github_created_at": repo.get("created_at", "")
            })

    print(f"    Found {len(repos)} repos, unique total: {len(all_github_repos)}")

github_discovered_df = pd.DataFrame(all_github_repos)
print(f"\n✓ Discovered {len(github_discovered_df)} unique MCP repos from GitHub")

# Show top repos by stars
if len(github_discovered_df) > 0:
    top_repos = github_discovered_df.nlargest(10, "github_stars")[["name", "author", "github_stars", "github_language"]]
    print("\nTop 10 MCP repos by stars:")
    display(top_repos)
