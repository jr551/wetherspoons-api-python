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

**Quick start (uvx):**

```bash
uvx --from wetherspoons-api-python[mcp] wetherspoons-mcp
```

**Available MCP tools:**
- `get_venues` - Fetch all Wetherspoons venues
- `get_venue_details` - Get detailed venue information
- `get_menus` - Fetch menus for a sales area
- `get_menu_details` - Get detailed menu information
- `get_drinks` - Fetch drinks with price per unit calculation

**MCP client configuration:**
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

Or for development:

```bash
git clone https://github.com/slack2450/wetherspoons-api.git
cd wetherspoons-api-python
pip install -e .
```

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
