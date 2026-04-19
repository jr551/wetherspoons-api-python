# MCP Server for Wetherspoons API

This is an MCP (Model Context Protocol) server for the Wetherspoons API. MCP is an open standard that allows AI systems to use tools and resources in a standardized way.

## Installation

No installation required! Use uvx to run the server with built-in dependencies:

```bash
uvx mcp-server/mcp-server.py
```

Or if you prefer traditional installation:

```bash
# Install MCP SDK
pip install mcp

# Clone this repository
git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python
```

## Usage

### Running the server (recommended - uvx)

```bash
uvx mcp-server/mcp-server.py
```

### Running the server (traditional)

```bash
python mcp-server.py
```

### Available Tools

The MCP server provides the following tools:

1. **get_venues** - Fetch all Wetherspoons venues that are currently open
2. **get_venue_details** - Get detailed information about a specific venue
3. **get_menus** - Fetch all menus for a specific sales area in a venue
4. **get_menu_details** - Get detailed menu information including all products and categories
5. **get_drinks** - Fetch all drinks with price per unit calculation, sorted by best value

### Configuration

The server automatically clones the wetherspoons-api-python repository to `/tmp/wetherspoons-api-python` if it doesn't exist.

### Using with MCP-compatible clients

Add this server to your MCP client configuration:

```json
{
  "mcpServers": {
    "wetherspoons": {
      "command": "python",
      "args": ["/path/to/mcp-server.py"]
    }
  }
}
```

## Legal Disclaimer

**THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY.**

This software is intended solely for research, educational, and informational purposes. There is no intention to harm JD Wetherspoon plc, interfere with their business operations, or violate their terms of service.

The authors and contributors of this software:
- Are not affiliated with, endorsed by, or connected to JD Wetherspoon plc in any way
- Do not authorize or condone the use of this software for any purpose that may violate terms of service or applicable laws
- Accept no responsibility or liability for how this software is used by third parties
- Make no warranties regarding the accuracy, completeness, or reliability of the data accessed through this API

Users of this software are solely responsible for ensuring their use complies with all applicable laws, terms of service, and regulations. The authors disclaim all liability for any damages, legal issues, or consequences arising from the use of this software.

**USE AT YOUR OWN RISK.**
