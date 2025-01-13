# mcp-server-docs

A Model Context Protocol server that provides access to documentation across multiple repositories. This server allows LLMs to search and retrieve documentation content from markdown files.

## Features

- Browse documentation across multiple repositories
- Full markdown/MDX support with frontmatter parsing
- Automatic title and description extraction
- Documentation content exposed as MCP resources
- Search and fetch tools for documentation retrieval

## Installation

### Using uv

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-docs*.

### Using PIP

Install via pip:

```bash
pip install mcp-server-docs
```

## Usage

The server needs to know which repositories to crawl for documentation. Provide these as repository mappings:

```bash
# Using uvx
uvx mcp-server-docs "mcp=/path/to/mcp/docs,anthropic=/path/to/anthropic/docs"

# Using pip installation
python -m mcp_server_docs "mcp=/path/to/mcp/docs,anthropic=/path/to/anthropic/docs"
```

### Configure for Claude Desktop

Add to your Claude Desktop config:

**TODO: this is actually not working right now, need to publish the package to the registry**
```json
"mcpServers": {
  "docs": {
    "command": "uvx",
    "args": [
      "mcp-server-docs",
      "mcp=/path/to/mcp/docs,anthropic=/path/to/anthropic/docs"
    ]
  }
}
```

## Available Tools

- `fetch-documents`: Retrieve documentation content by repository and path
  - Search through available documentation files
  - Get documentation content with preserved structure
  - Support for fetching multiple related documents

## Resources

All documentation files are exposed as MCP resources with:
- URI format: `file://{repository}/{path}`
- Rich metadata including titles and descriptions
- Full markdown content

## Contributing

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/example-servers/

Pull requests welcome!
