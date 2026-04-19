"""
MCP Server for Wetherspoons API
"""

import asyncio
import json
import math
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from wetherspoons_api import venues, get_venue, get_menus, get_menu, get_drinks

# Create MCP server
app = Server("wetherspoons-api")


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371

    return c * r


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_venues",
            description="⚠️ WARNING: Returns up to 796 venues! Use search_venues tool first to find specific venues by name. Only use this tool when you need a large list with optional filters (search param for name filtering, limit param to cap results).",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Filter venues by name (case-insensitive partial match). HIGHLY RECOMMENDED to avoid 796 results."
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum venues to return (default: 50, max: 796). Reduce if filtering."
                    }
                },
            }
        ),
        Tool(
            name="search_venues",
            description="✅ RECOMMENDED FIRST STEP: Search for venues by name (e.g., 'The Watchman'). Returns matching venues with venue_ref needed for other tools. Always use this before get_venues when looking for a specific venue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Venue name or partial name to search for"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (default: 10)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="find_nearest_venues",
            description="Find Wetherspoons venues nearest to a given latitude/longitude location. Returns venues sorted by distance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "Latitude of your location (e.g., 51.5074 for London)"
                    },
                    "lng": {
                        "type": "number",
                        "description": "Longitude of your location (e.g., -0.1278 for London)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of venues to return (default: 10)"
                    }
                },
                "required": ["lat", "lng"]
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
    try:
        if name == "get_venues":
            result = venues()
            search = arguments.get("search", "").lower()
            limit = min(arguments.get("limit", 50), 796)
            
            # Filter by search term if provided
            if search:
                result = [v for v in result if search in v.name.lower()]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "total_count": len(result),
                    "showing": min(limit, len(result)),
                    "venues": [
                        {
                            "name": v.name,
                            "franchise": v.franchise,
                            "venue_ref": v.venue_ref,
                            "address": str(v.address) if v.address else None,
                            "location": {
                                "lat": v.address.location.latitude,
                                "lng": v.address.location.longitude
                            } if v.address and v.address.location else None
                        }
                        for v in result[:limit]
                    ]
                }, indent=2)
            )]

        elif name == "search_venues":
            search_name = arguments.get("name", "").lower()
            limit = arguments.get("limit", 10)
            result = venues()
            
            # Find matching venues
            matching = [v for v in result if search_name in v.name.lower()]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "search": arguments.get("name"),
                    "matches_found": len(matching),
                    "venues": [
                        {
                            "name": v.name,
                            "franchise": v.franchise,
                            "venue_ref": v.venue_ref,
                            "address": str(v.address) if v.address else None,
                            "location": {
                                "lat": v.address.location.latitude,
                                "lng": v.address.location.longitude
                            } if v.address and v.address.location else None
                        }
                        for v in matching[:limit]
                    ]
                }, indent=2)
            )]

        elif name == "find_nearest_venues":
            user_lat = arguments["lat"]
            user_lng = arguments["lng"]
            limit = arguments.get("limit", 10)
            
            # Get all venues with location
            all_venues = venues()
            venues_with_location = [
                v for v in all_venues 
                if v.address and v.address.location
            ]
            
            # Calculate distance for each venue
            venues_with_distance = []
            for venue in venues_with_location:
                venue_lat = venue.address.location.latitude
                venue_lng = venue.address.location.longitude
                distance_km = _haversine_distance(user_lat, user_lng, venue_lat, venue_lng)
                venues_with_distance.append((venue, distance_km))
            
            # Sort by distance and take nearest
            venues_with_distance.sort(key=lambda x: x[1])
            nearest = venues_with_distance[:limit]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "user_location": {"lat": user_lat, "lng": user_lng},
                    "total_venues_checked": len(venues_with_location),
                    "venues": [
                        {
                            "name": v.name,
                            "franchise": v.franchise,
                            "venue_ref": v.venue_ref,
                            "address": str(v.address) if v.address else None,
                            "location": {
                                "lat": v.address.location.latitude,
                                "lng": v.address.location.longitude
                            },
                            "distance_km": round(distance, 2)
                        }
                        for v, distance in nearest
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
                    "sales_areas": result.sales_areas,
                    "location": {
                        "lat": venue.address.location.latitude,
                        "lng": venue.address.location.longitude
                    } if venue.address and venue.address.location else None
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
            
            # Build structured food output by category
            food_categories = []
            for category in result.data.get("categories", []):
                items = []
                for item_group in category.get("itemGroups", []):
                    for item in item_group.get("items", []):
                        # Get price from first portion option
                        portions = item.get("portionOptions", [])
                        price_pounds = None
                        price_pence = None
                        price_gbp = None
                        if portions:
                            price_pounds = portions[0].get("value", {}).get("price", {}).get("value")
                            if price_pounds:
                                price_pence = int(price_pounds * 100)
                                price_gbp = f"£{price_pounds:.2f}"
                        
                        items.append({
                            "name": item.get("name"),
                            "price_pounds": price_pounds,
                            "price_pence": price_pence,
                            "price_gbp": price_gbp,
                            "description": item.get("description", "")[:100]  # Truncate long descriptions
                        })
                
                if items:  # Only add categories with items
                    food_categories.append({
                        "category": category.get("name"),
                        "item_count": len(items),
                        "items": items[:5]  # First 5 items per category
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "menu_name": result.data.get("name", "Unknown"),
                    "categories_count": len(food_categories),
                    "categories": food_categories[:10]  # Top 10 categories
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
                            "price_pounds": d.price,
                            "price_pence": int(d.price * 100),
                            "units": d.units,
                            "price_per_unit_pence": round(d.ppu, 2),
                            "price_gbp": f"£{d.price:.2f}"
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
