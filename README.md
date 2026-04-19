# Wetherspoons API - Python

A Python package for accessing JD Wetherspoon's venue and menu data, including drink information with pricing and alcohol unit calculations.

This is a Python port of the original TypeScript package by [Joss Bird](https://github.com/slack2450/wetherspoons-api).

## ⚠️ Disclaimer

**THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY.**

This is a Python port of the original TypeScript package created by [Joss Bird](https://github.com/slack2450/wetherspoons-api). The original work serves as the foundation for this implementation.

**Research Purposes Only:**
This software is intended solely for research, educational, and informational purposes. There is no intention to harm JD Wetherspoon plc, interfere with their business operations, or violate their terms of service.

The authors and contributors of this software:
- Are not affiliated with, endorsed by, or connected to JD Wetherspoon plc in any way
- Do not authorize or condone the use of this software for any purpose that may violate terms of service or applicable laws
- Accept no responsibility or liability for how this software is used by third parties
- Make no warranties regarding the accuracy, completeness, or reliability of the data accessed through this API

Users of this software are solely responsible for ensuring their use complies with all applicable laws, terms of service, and regulations. The authors disclaim all liability for any damages, legal issues, or consequences arising from the use of this software.

**USE AT YOUR OWN RISK.**

## Installation

```bash
pip install wetherspoons-api-python
```

## MCP Server (Open Standard)

This package includes an MCP (Model Context Protocol) server that provides an open standard interface for the Wetherspoons API. MCP is compatible with various AI systems, not just Claude.

### Quick Start

**Using uvx (recommended):**
```bash
uvx --from wetherspoons-api-python[mcp] wetherspoons-mcp
```

**MCP Client Configuration:**
```json
{
  "mcpServers": {
    "wetherspoons": {
      "command": "uvx",
      "args": ["--from", "wetherspoons-api-python[mcp]", "wetherspoons-mcp"]
    }
  }
}
```

### Available MCP Tools

#### 1. search_venues ✅ **RECOMMENDED FIRST**
Search for venues by name. Returns matching venues with venue_ref needed for other tools.

**Parameters:**
- `name` (required): Venue name or partial name (e.g., "The Watchman")
- `limit` (optional): Maximum results (default: 10)

**Example:**
```json
{
  "name": "The Watchman",
  "limit": 5
}
```

**Response:**
```json
{
  "search": "The Watchman",
  "matches_found": 1,
  "venues": [
    {
      "name": "The Watchman",
      "franchise": "lloyds",
      "venue_ref": 5447,
      "address": "The Old Post Office...",
      "location": {"lat": 51.4015, "lng": -0.2582}
    }
  ]
}
```

#### 2. get_venues
⚠️ **WARNING:** Returns up to 796 venues. Use with `search` param to filter.

**Parameters:**
- `search` (optional): Filter by name (case-insensitive)
- `limit` (optional): Max venues (default: 50, max: 796)

**Example:**
```json
{
  "search": "London",
  "limit": 20
}
```

#### 3. find_nearest_venues
Find venues nearest to GPS coordinates. Returns venues sorted by distance.

**Parameters:**
- `lat` (required): Latitude (e.g., 51.5074 for London)
- `lng` (required): Longitude (e.g., -0.1278 for London)
- `limit` (optional): Max results (default: 10)

**Example:**
```json
{
  "lat": 51.5,
  "lng": -0.12,
  "limit": 5
}
```

**Response:**
```json
{
  "user_location": {"lat": 51.5, "lng": -0.12},
  "venues": [
    {
      "name": "The Lion & The Unicorn",
      "venue_ref": 1234,
      "location": {"lat": 51.501, "lng": -0.125},
      "distance_km": 0.65
    }
  ]
}
```

#### 4. get_venue_details
Get detailed venue information including sales areas and ordering capabilities.

**Parameters:**
- `venue_ref` (required): Venue reference number from search

**Example:**
```json
{
  "venue_ref": 5447
}
```

**Response:**
```json
{
  "name": "The Watchman",
  "can_place_order": true,
  "venue_can_order": true,
  "sales_areas": [
    {"id": 1234, "name": "Bar", "isMenuAvailable": true}
  ],
  "location": {"lat": 51.4015, "lng": -0.2582}
}
```

#### 5. get_menus
Fetch all menus for a specific sales area in a venue.

**Parameters:**
- `venue_ref` (required): Venue reference
- `sales_area_id` (required): Sales area ID from venue details

**Example:**
```json
{
  "venue_ref": 5447,
  "sales_area_id": 1234
}
```

**Response:**
```json
[
  {"name": "Drinks", "can_order": true, "id": 5678},
  {"name": "Food", "can_order": true, "id": 5679}
]
```

#### 6. get_menu_details
Get detailed menu information including all items with prices.

**Parameters:**
- `menu_id` (required): Menu ID from get_menus

**Example:**
```json
{
  "menu_id": 5678
}
```

**Response:**
```json
{
  "menu_name": "Food",
  "categories_count": 17,
  "categories": [
    {
      "category": "Deli Deals",
      "item_count": 5,
      "items": [
        {
          "name": "Cheeseburger",
          "price_pounds": 5.99,
          "price_pence": 599,
          "price_gbp": "£5.99",
          "description": "Classic beef burger..."
        }
      ]
    }
  ]
}
```

#### 7. get_drinks
Fetch all drinks with alcohol units and price per unit analysis.

**Parameters:**
- `venue_ref` (required): Venue reference
- `sales_area_id` (required): Sales area ID

**Example:**
```json
{
  "venue_ref": 5447,
  "sales_area_id": 1234
}
```

**Response:**
```json
{
  "count": 171,
  "drinks": [
    {
      "name": "Ruddles Best",
      "price_pounds": 2.49,
      "price_pence": 249,
      "units": 2.27,
      "price_per_unit_pence": 109.69,
      "price_gbp": "£2.49"
    }
  ]
}
```

### Recommended Workflow

**1. Find a Venue:**
Use `search_venues` to find the venue and get its `venue_ref`.

**2. Get Venue Details:**
Use `get_venue_details` with the `venue_ref` to get sales area IDs.

**3. Get Drinks/Food:**
Use `get_drinks` or `get_menu_details` with `venue_ref` and `sales_area_id`.

### Complete Example

**Finding best value drinks at a specific pub:**

```json
// Step 1: Search for the venue
{
  "tool": "search_venues",
  "arguments": {
    "name": "The Watchman"
  }
}
// Returns: venue_ref = 5447

// Step 2: Get venue details to find sales_area_id
{
  "tool": "get_venue_details",
  "arguments": {
    "venue_ref": 5447
  }
}
// Returns: sales_areas = [{"id": 1234, "name": "Bar"}]

// Step 3: Get drinks sorted by best value
{
  "tool": "get_drinks",
  "arguments": {
    "venue_ref": 5447,
    "sales_area_id": 1234
  }
}
// Returns: List of drinks with price per unit, sorted by value
```

### Notes

- All prices are returned in **pounds** (e.g., 1.62 = £1.62), not pence
- Alcohol units use UK standard: 1 unit = 10ml pure alcohol
- Drinks are sorted by price per unit (best value first)
- GPS coordinates use WGS84 (decimal degrees)

## Features

- 🏪 Fetch all Wetherspoons venues
- 📍 Get detailed venue information
- 🍺 Access venue menus and drinks
- 💰 Calculate price per unit (PPU) for alcoholic beverages
- ✅ Type-safe with Pydantic validation
- 🔄 Automatic handling of different portion sizes

## Usage

### Get All Venues

```python
from wetherspoons_api import venues

all_venues = venues()
print(all_venues)
# [
#   HighLevelVenue(franchise='lloyds', id=123, is_closed=False, 
#                 name='The Moon Under Water', venue_ref=456),
#   ...
# ]
```

### Get Venue Details

```python
from wetherspoons_api import venues, get_venue

all_venues = venues()
venue = all_venues[0]
details = get_venue(venue)

print(details)
# DetailedVenue(can_place_order=True, franchise='lloyds', id=123,
#              name='The Moon Under Water', sales_areas=[{'id': 789}],
#              venue_can_order=True, venue_ref=456)
```

### Get Drinks with Price Analysis

```python
from wetherspoons_api import venues, get_drinks

all_venues = venues()
venue = all_venues[0]
drinks = get_drinks(venue)

print(drinks)
# [
#   Drink(name='Ruddles Best', units=2.27, product_id=12345,
#         price=249, ppu=109.69),
#   ...
# ]
# Sorted by best value (lowest price per unit first)
```

**Alcohol Units Calculation (UK Standard):**
- 1 unit = 10ml of pure alcohol
- Formula: `units = (volume_ml × ABV%) / 1000`
- Examples:
  - 25ml vodka at 40% = 1.0 unit (standard single measure)
  - 568ml pint at 4% = 2.27 units
  - 175ml wine at 12% = 2.1 units

**Price Per Unit (PPU):** Lower is better value. Calculated as `price_pence / units`.

### Get Menus

```python
from wetherspoons_api import venues, get_venue, get_menus, get_menu

all_venues = venues()
venue = all_venues[0]
details = get_venue(venue)

# Get all menus for a sales area
menus = get_menus(details, details.sales_areas[0]['id'])

# Get detailed menu information
drinks_menu = next((m for m in menus if m.name == 'Drinks'), None)
if drinks_menu:
    detailed_menu = get_menu(drinks_menu)
    print(detailed_menu.data['categories'])
```

## Common Pitfalls

When using this API, watch out for these common mistakes:

### 1. API is Synchronous (Not Async)

❌ **Wrong:**
```python
# Don't use async/await
venues = await venues()  # TypeError: object list can't be used in 'await' expression
```

✅ **Correct:**
```python
# All API functions are synchronous
from wetherspoons_api import venues
all_venues = venues()
```

### 2. Python Uses Snake_Case (Not CamelCase)

❌ **Wrong:**
```python
details.salesAreas  # AttributeError: 'DetailedVenue' object has no attribute 'salesAreas'
```

✅ **Correct:**
```python
details.sales_areas  # Snake case with underscores
```

### 3. sales_areas Returns Dictionaries (Not Objects)

❌ **Wrong:**
```python
sales_area = details.sales_areas[0]
sales_area.name  # AttributeError: 'dict' object has no attribute 'name'
```

✅ **Correct:**
```python
sales_area = details.sales_areas[0]
sales_area['id']  # Use dict key access: ['id'], ['name'], etc.
```

### 4. get_drinks Takes One Argument (Not Two)

❌ **Wrong:**
```python
# Don't pass sales_area_id separately
drinks = get_drinks(venue, sales_area_id)  # TypeError: takes 1 positional argument but 2 were given
```

✅ **Correct:**
```python
# Pass only the venue object - get_drinks handles sales area lookup internally
drinks = get_drinks(venue)
```

## API Reference

### Functions

#### `venues() -> List[HighLevelVenue]`
Fetches all Wetherspoons venues.

**Returns:** List of venue objects with basic information.

#### `get_venue(venue: HighLevelVenue) -> DetailedVenue`
Gets detailed information about a specific venue.

**Parameters:**
- `venue`: A venue object from `venues()`

**Returns:** Detailed venue information including sales areas and ordering capabilities.

#### `get_menus(venue: DetailedVenue, sales_area_id: int) -> List[HighLevelMenu]`
Fetches all menus for a specific sales area in a venue.

**Parameters:**
- `venue`: A detailed venue object from `get_venue()`
- `sales_area_id`: The ID of the sales area

**Returns:** List of menu objects.

#### `get_menu(high_level_menu: HighLevelMenu) -> DetailedMenu`
Gets detailed menu information including all products and categories.

**Parameters:**
- `high_level_menu`: A menu object from `get_menus()`

**Returns:** Detailed menu with categories, item groups, and products.

#### `get_drinks(high_level_venue: HighLevelVenue) -> List[Drink]`
Fetches all drinks from a venue's drinks menu, calculates alcohol units and price per unit, then sorts by best value.

**Parameters:**
- `high_level_venue`: A venue object from `venues()`

**Returns:** List of drinks sorted by price per unit (best value first).

### Models

#### `HighLevelVenue`
```python
class HighLevelVenue:
    franchise: str
    id: int
    is_closed: bool
    name: str
    venue_ref: int
    address: Optional[Address]
```

#### `DetailedVenue`
```python
class DetailedVenue:
    can_place_order: Optional[bool]
    franchise: str
    id: int
    is_closed: Optional[bool]
    name: str
    sales_areas: List[dict]
    venue_can_order: Optional[bool]
    venue_ref: Union[str, int]
    address: Optional[Address]
```

#### `Drink`
```python
class Drink:
    name: str
    units: float        # Alcohol units
    product_id: int
    price: int          # Price in pence
    ppu: float          # Price per unit in pence
```

## How It Works

The package:
1. Connects to the JD Wetherspoon API
2. Validates all responses using Pydantic models for type safety
3. Calculates alcohol units based on ABV and volume information
4. Determines the best value portion size for each drink
5. Sorts drinks by price per unit to help find the best deals

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest

# Run tests with coverage
pytest --cov=wetherspoons_api --cov-report=html

# Run specific test
pytest tests/test_api.py::TestVenues::test_venues_filters_open_venues
```

## Testing

The package includes comprehensive unit tests with pytest. Tests use mocking to avoid hitting the live API during development.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=wetherspoons_api
```

## License

MIT © [Joss Bird](https://github.com/slack2450) - Original TypeScript version

Python port maintains the same MIT license.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

Report bugs and feature requests at [https://github.com/slack2450/wetherspoons-api/issues](https://github.com/slack2450/wetherspoons-api/issues)

## Original TypeScript Version

This is a Python port of the original [wetherspoons-api](https://github.com/slack2450/wetherspoons-api) TypeScript package.
