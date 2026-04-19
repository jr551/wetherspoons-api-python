#!/usr/bin/env python3
"""
MCP Server for Wetherspoons API
An open standard server that can be used with any MCP-compatible AI system
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sys

from wetherspoons_api import venues, get_venue, get_menus, get_menu, get_drinks

# Create MCP server
app = Server("wetherspoons-api")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_venues",
            description="Fetch all Wetherspoons venues that are currently open",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_venue_details",
            description="Get detailed information about a specific venue",
            inputSchema={
                "type": "object",
                "properties": {
                    "venue_ref": {
                        "type": "number",
                        "description": "Venue reference number"
                    }
                },
                "required": ["venue_ref"]
            }
        ),
        Tool(
            name="get_menus",
            description="Fetch all menus for a specific sales area in a venue",
            inputSchema={
                "type": "object",
                "properties": {
                    "venue_ref": {
                        "type": "number",
                        "description": "Venue reference number"
                    },
                    "sales_area_id": {
                        "type": "number",
                        "description": "Sales area ID"
                    }
                },
                "required": ["venue_ref", "sales_area_id"]
            }
        ),
        Tool(
            name="get_menu_details",
            description="Get detailed menu information including all products and categories",
            inputSchema={
                "type": "object",
                "properties": {
                    "menu_id": {
                        "type": "number",
                        "description": "Menu ID"
                    }
                },
                "required": ["menu_id"]
            }
        ),
        Tool(
            name="get_drinks",
            description="Fetch all drinks from a venue's drinks menu with price per unit calculation, sorted by best value",
            inputSchema={
                "type": "object",
                "properties": {
                    "venue_ref": {
                        "type": "number",
                        "description": "Venue reference number"
                    },
                    "sales_area_id": {
                        "type": "number",
                        "description": "Sales area ID"
                    }
                },
                "required": ["venue_ref", "sales_area_id"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    # Ensure repo is cloned
    import subprocess
    import os
    
    if not os.path.exists('/tmp/wetherspoons-api-python'):
        subprocess.run([
            'git', 'clone',
            'https://github.com/jr551/wetherspoons-api-python.git',
            '/tmp/wetherspoons-api-python'
        ], check=True)
    
    try:
        if name == "get_venues":
            result = venues()
            return [TextContent(
                type="text",
                text=json.dumps({
                    "count": len(result),
                    "venues": [
                        {
                            "name": v.name,
                            "franchise": v.franchise,
                            "venue_ref": v.venue_ref,
                            "address": str(v.address) if v.address else None
                        }
                        for v in result[:10]  # Return first 10
                    ]
                }, indent=2)
            )]
        
        elif name == "get_venue_details":
            venue_ref = arguments["venue_ref"]
            # First get the high-level venue
            all_venues = venues()
            venue = next((v for v in all_venues if v.venue_ref == venue_ref), None)
            if not venue:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Venue not found"}, indent=2)
                )]
            result = get_venue(venue)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "name": result.name,
                    "can_place_order": result.can_place_order,
                    "venue_can_order": result.venue_can_order,
                    "sales_areas": result.sales_areas
                }, indent=2, default=str)
            )]
        
        elif name == "get_menus":
            venue_ref = arguments["venue_ref"]
            sales_area_id = arguments["sales_area_id"]
            # First get the high-level venue
            all_venues = venues()
            venue = next((v for v in all_venues if v.venue_ref == venue_ref), None)
            if not venue:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Venue not found"}, indent=2)
                )]
            result = get_menus(get_venue(venue), sales_area_id)
            return [TextContent(
                type="text",
                text=json.dumps([
                    {
                        "name": m.name,
                        "can_order": m.can_order,
                        "id": m.id
                    }
                    for m in result
                ], indent=2)
            )]
        
        elif name == "get_menu_details":
            menu_id = arguments["menu_id"]
            result = get_menu(type('obj', (object,), {'id': menu_id}))
            return [TextContent(
                type="text",
                text=json.dumps({
                    "categories_count": len(result.data.get("categories", [])),
                    "categories": [
                        {
                            "name": c.get("name"),
                            "item_groups_count": len(c.get("itemGroups", []))
                        }
                        for c in result.data.get("categories", [])[:5]
                    ]
                }, indent=2)
            )]
        
        elif name == "get_drinks":
            venue_ref = arguments["venue_ref"]
            sales_area_id = arguments["sales_area_id"]
            # First get the high-level venue
            all_venues = venues()
            venue = next((v for v in all_venues if v.venue_ref == venue_ref), None)
            if not venue:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Venue not found"}, indent=2)
                )]
            result = get_drinks(venue)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "count": len(result),
                    "drinks": [
                        {
                            "name": d.name,
                            "price_pence": d.price,
                            "units": d.units,
                            "price_per_unit_pence": round(d.ppu, 2),
                            "price_gbp": f"£{d.price/100:.2f}"
                        }
                        for d in result[:10]  # Return top 10 best value
                    ]
                }, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
