#!/usr/bin/env python3
"""Entry point for wetherspoons-mcp"""

import asyncio
from wetherspoons_mcp.server import main as server_main


def main():
    """Entry point for console script"""
    asyncio.run(server_main())


if __name__ == "__main__":
    main()
