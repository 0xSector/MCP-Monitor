# Cell 4: Curated Server List
# Manual list of notable MCP servers from major companies

# This can be replaced with an Input Table in Hex for easy editing
CURATED_SERVERS = [
    {
        "name": "Stripe MCP Server",
        "repository": "https://github.com/stripe/agent-toolkit",
        "npm_package": "@stripe/agent-toolkit",
        "pypi_package": "stripe-agent-toolkit",
        "company": "Stripe",
        "category": "payments,fintech"
    },
    {
        "name": "Cloudflare MCP Server",
        "repository": "https://github.com/cloudflare/mcp-server-cloudflare",
        "npm_package": "@cloudflare/mcp-server-cloudflare",
        "pypi_package": None,
        "company": "Cloudflare",
        "category": "infrastructure,cdn"
    },
    {
        "name": "Notion MCP Server",
        "repository": "https://github.com/makenotion/notion-mcp-server",
        "npm_package": None,
        "pypi_package": None,
        "company": "Notion",
        "category": "productivity,notes"
    },
    {
        "name": "Sentry MCP Server",
        "repository": "https://github.com/getsentry/sentry-mcp",
        "npm_package": None,
        "pypi_package": "sentry-mcp",
        "company": "Sentry",
        "category": "monitoring,devtools"
    },
    {
        "name": "Browserbase MCP Server",
        "repository": "https://github.com/browserbase/mcp-server-browserbase",
        "npm_package": "@browserbase/mcp-server-browserbase",
        "pypi_package": None,
        "company": "Browserbase",
        "category": "browser,automation"
    },
    {
        "name": "Neon MCP Server",
        "repository": "https://github.com/neondatabase/mcp-server-neon",
        "npm_package": "@neondatabase/mcp-server-neon",
        "pypi_package": None,
        "company": "Neon",
        "category": "database,postgres"
    },
    {
        "name": "Axiom MCP Server",
        "repository": "https://github.com/axiomhq/mcp-server-axiom",
        "npm_package": "@axiomhq/mcp-server-axiom",
        "pypi_package": None,
        "company": "Axiom",
        "category": "observability,logging"
    },
    {
        "name": "Raygun MCP Server",
        "repository": "https://github.com/MindscapeHQ/mcp-server-raygun",
        "npm_package": "@anthropic/mcp-server-raygun",
        "pypi_package": None,
        "company": "Raygun",
        "category": "monitoring,errors"
    },
    {
        "name": "Tinybird MCP Server",
        "repository": "https://github.com/tinybirdco/mcp-tinybird",
        "npm_package": None,
        "pypi_package": "mcp-tinybird",
        "company": "Tinybird",
        "category": "analytics,data"
    },
    {
        "name": "Linear MCP Server",
        "repository": "https://github.com/jerhadf/linear-mcp-server",
        "npm_package": "linear-mcp-server",
        "pypi_package": None,
        "company": "Linear",
        "category": "project-management,issues"
    },
    {
        "name": "Slack MCP Server",
        "repository": "https://github.com/modelcontextprotocol/servers",
        "npm_package": "@modelcontextprotocol/server-slack",
        "pypi_package": None,
        "company": "Anthropic",
        "category": "communication,chat"
    },
    {
        "name": "GitHub MCP Server",
        "repository": "https://github.com/modelcontextprotocol/servers",
        "npm_package": "@modelcontextprotocol/server-github",
        "pypi_package": None,
        "company": "Anthropic",
        "category": "devtools,git"
    },
    {
        "name": "Filesystem MCP Server",
        "repository": "https://github.com/modelcontextprotocol/servers",
        "npm_package": "@modelcontextprotocol/server-filesystem",
        "pypi_package": None,
        "company": "Anthropic",
        "category": "filesystem,core"
    },
    {
        "name": "PostgreSQL MCP Server",
        "repository": "https://github.com/modelcontextprotocol/servers",
        "npm_package": "@modelcontextprotocol/server-postgres",
        "pypi_package": None,
        "company": "Anthropic",
        "category": "database,sql"
    },
    {
        "name": "Brave Search MCP Server",
        "repository": "https://github.com/modelcontextprotocol/servers",
        "npm_package": "@modelcontextprotocol/server-brave-search",
        "pypi_package": None,
        "company": "Anthropic",
        "category": "search,web"
    }
]

# Convert to DataFrame
curated_servers_df = pd.DataFrame(CURATED_SERVERS)

# Normalize columns to match other sources
curated_servers_df["server_id"] = curated_servers_df["name"].str.lower().str.replace(" ", "_")
curated_servers_df["description"] = curated_servers_df["company"] + " official MCP server"
curated_servers_df["author"] = curated_servers_df["company"]
curated_servers_df["version"] = ""
curated_servers_df["source"] = "curated"
curated_servers_df["discovered_date"] = datetime.now().strftime("%Y-%m-%d")
curated_servers_df["categories"] = curated_servers_df["category"]

# Select standard columns
curated_servers_df = curated_servers_df[[
    "server_id", "name", "description", "repository",
    "npm_package", "pypi_package", "categories", "author",
    "version", "source", "discovered_date", "company"
]]

print(f"✓ Loaded {len(curated_servers_df)} curated servers")
display(curated_servers_df[["name", "company", "npm_package", "pypi_package"]])
