# Wetherspoons API - Data Models Reference

Complete reference of all data structures and models exposed by the Wetherspoons API Python library.

## Core Models

### HighLevelVenue

Basic venue information returned by `venues()`.

```python
@dataclass
class HighLevelVenue:
    franchise: str      # e.g., "lloyds"
    id: int            # Internal venue ID
    is_closed: bool    # Whether venue is currently closed
    name: str          # e.g., "The Moon Under Water"
    venue_ref: int     # Public venue reference number (used in other calls)
    address: Address   # Full address with GPS coordinates
```

**Example:**
```python
from wetherspoons_api import venues

all_venues = venues()
venue = all_venues[0]

print(venue.name)        # "The Moon Under Water"
print(venue.venue_ref)   # 1234
print(venue.franchise)   # "lloyds"
print(venue.is_closed)   # False
```

### DetailedVenue

Extended venue information returned by `get_venue()`.

```python
@dataclass
class DetailedVenue:
    can_place_order: bool    # Can orders be placed?
    franchise: str           # e.g., "lloyds"
    id: int                  # Internal venue ID
    is_closed: bool          # Whether venue is closed
    name: str                # Venue name
    sales_areas: List[dict]  # Available sales areas with IDs
    venue_can_order: bool    # Venue accepts orders
    venue_ref: Union[str, int]  # Public reference
    address: Address         # Full address
```

**Sales Areas Structure:**
```python
[
    {
        'id': 789,                    # Sales area ID (needed for menus)
        'name': 'Bar',                # Sales area name
        'tableService': True,
        'isMenuAvailable': True
    }
]
```

**Example:**
```python
from wetherspoons_api import venues, get_venue

all_venues = venues()
venue = all_venues[0]
details = get_venue(venue)

print(details.name)              # "The Moon Under Water"
print(details.can_place_order)   # True
print(details.sales_areas)       # [{'id': 789, 'name': 'Bar', ...}]

# Get first sales area ID for menu calls
sales_area_id = details.sales_areas[0]['id']
```

### Address

Complete address with GPS coordinates.

```python
@dataclass
class Address:
    line1: Optional[str]      # Street address line 1
    line2: Optional[str]      # Street address line 2
    line3: Optional[str]      # Street address line 3
    town: Optional[str]       # Town/City
    county: Optional[str]     # County
    postcode: Optional[str]   # Postcode
    country: Optional[Country]  # Country info
    location: Optional[Location]  # GPS coordinates
```

**Example:**
```python
address = venue.address

print(address.line1)       # "28-30 The Mall"
print(address.town)        # "London"
print(address.postcode)    # "SW1A 1AA"

# GPS coordinates
if address.location:
    print(address.location.latitude)   # 51.5074
    print(address.location.longitude)  # -0.1278
```

### Location

GPS coordinates for mapping.

```python
@dataclass
class Location:
    latitude: float       # Latitude (e.g., 51.5074)
    longitude: float      # Longitude (e.g., -0.1278)
    distance_tolerance: Optional[float]  # Search radius if applicable
```

### HighLevelMenu

Basic menu information.

```python
@dataclass
class HighLevelMenu:
    can_order: bool       # Can orders be placed on this menu?
    franchise: str        # Venue franchise
    id: int              # Menu ID
    name: str            # Menu name (e.g., "Drinks", "Food")
    sales_area_id: int   # Associated sales area
    venue_ref: int       # Venue reference
```

**Example:**
```python
from wetherspoons_api import get_menus

menus = get_menus(details, sales_area_id)
for menu in menus:
    print(f"{menu.name} (ID: {menu.id})")
    # Drinks (ID: 12345)
    # Food (ID: 12346)
```

### DetailedMenu

Complete menu with all items and categories.

```python
@dataclass
class DetailedMenu:
    data: Dict  # Full menu data structure
```

**Data Structure:**
```python
{
    'name': 'Drinks',
    'categories': [
        {
            'name': 'Real Ales',
            'itemGroups': [
                {
                    'items': [
                        {
                            'id': 12345,
                            'name': 'Ruddles Best',
                            'description': '3.7% ABV, 1 unit',
                            'portionOptions': [
                                {
                                    'label': 'Pint',
                                    'value': {
                                        'price': {
                                            'value': 2.49,  # Pounds
                                            'currency': 'GBP'
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

### Drink

Analyzed drink with alcohol units and value metrics.

```python
@dataclass
class Drink:
    name: str          # Drink name
    units: float       # Alcohol units (UK standard)
    product_id: int    # Product ID
    price: float       # Price in POUNDS (e.g., 1.62)
    ppu: float         # Price per unit in pence
```

**Important:** Price is in **pounds**, not pence. For example:
- `price: 1.62` = £1.62
- `price: 2.49` = £2.49

**Example:**
```python
from wetherspoons_api import get_drinks

drinks = get_drinks(venue)
for drink in drinks[:5]:
    print(f"{drink.name}: £{drink.price:.2f}")
    print(f"  Units: {drink.units:.2f}")
    print(f"  Price per unit: {drink.ppu:.0f}p")
    
# Ruddles Best: £2.49
#   Units: 2.27
#   Price per unit: 110p
```

## Complete Usage Examples

### Example 1: Find Nearest Pub

```python
from wetherspoons_api import venues
import math

def find_nearest(user_lat: float, user_lng: float, limit: int = 5):
    """Find nearest venues using Haversine formula."""
    
    def haversine(lat1, lng1, lat2, lng2):
        R = 6371  # Earth radius in km
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        return 2 * R * math.asin(math.sqrt(a))
    
    all_venues = venues()
    venues_with_distance = []
    
    for venue in all_venues:
        if venue.address and venue.address.location:
            v_lat = venue.address.location.latitude
            v_lng = venue.address.location.longitude
            distance = haversine(user_lat, user_lng, v_lat, v_lng)
            venues_with_distance.append((venue, distance))
    
    # Sort by distance and return nearest
    venues_with_distance.sort(key=lambda x: x[1])
    return venues_with_distance[:limit]

# Find nearest pubs to Central London
nearest = find_nearest(51.5074, -0.1278, 3)
for venue, distance in nearest:
    print(f"{venue.name}: {distance:.2f} km away")
```

### Example 2: Get Best Value Drinks

```python
from wetherspoons_api import venues, get_drinks

# Get all venues
all_venues = venues()

# Search for specific venue
watchman = next((v for v in all_venues if "Watchman" in v.name), None)

if watchman:
    # Get drinks sorted by value
    drinks = get_drinks(watchman)
    
    print(f"Top 5 best value drinks at {watchman.name}:")
    for drink in drinks[:5]:
        print(f"  {drink.name}")
        print(f"    Price: £{drink.price:.2f}")
        print(f"    Units: {drink.units:.2f}")
        print(f"    Value: {drink.ppu:.0f}p per unit")
        print()
```

### Example 3: Get Food Menu with Prices

```python
from wetherspoons_api import venues, get_venue, get_menus, get_menu

all_venues = venues()
venue = all_venues[0]
details = get_venue(venue)

# Get menus for first sales area
sales_area_id = details.sales_areas[0]['id']
menus = get_menus(details, sales_area_id)

# Find food menu
food_menu = next((m for m in menus if "Food" in m.name), None)

if food_menu:
    detailed = get_menu(food_menu)
    
    for category in detailed.data.get('categories', [])[:5]:
        print(f"\n{category['name']}:")
        
        for item_group in category.get('itemGroups', [])[:2]:
            for item in item_group.get('items', [])[:3]:
                name = item.get('name')
                portions = item.get('portionOptions', [])
                if portions:
                    price = portions[0].get('value', {}).get('price', {}).get('value')
                    if price:
                        print(f"  - {name}: £{price:.2f}")
```

### Example 4: Venue Search with Filters

```python
from wetherspoons_api import venues

all_venues = venues()

# Filter by name
london_venues = [v for v in all_venues 
                 if "London" in v.address.town 
                 and not v.is_closed]

# Filter by franchise
lloyds_venues = [v for v in all_venues 
                 if v.franchise == "lloyds"]

# Get venues with GPS coordinates
mappable_venues = [v for v in all_venues 
                   if v.address 
                   and v.address.location]

print(f"Total venues: {len(all_venues)}")
print(f"In London: {len(london_venues)}")
print(f"Lloyds brand: {len(lloyds_venues)}")
print(f"With coordinates: {len(mappable_venues)}")
```

## MCP Server Tool Reference

### get_venues
Returns venues list with optional search filter.

**Parameters:**
- `search` (optional): Filter by name (case-insensitive)
- `limit` (optional): Max venues to return (default: 50)

**Returns:**
```json
{
  "total_count": 796,
  "showing": 50,
  "venues": [
    {
      "name": "The Moon Under Water",
      "franchise": "lloyds",
      "venue_ref": 1234,
      "address": "28-30 The Mall, London...",
      "location": {"lat": 51.5074, "lng": -0.1278}
    }
  ]
}
```

### search_venues
Search for venues by name.

**Parameters:**
- `name` (required): Search term
- `limit` (optional): Max results (default: 10)

**Returns:** Same structure as get_venues with `matches_found` field.

### find_nearest_venues
Find nearest venues to GPS coordinates.

**Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `limit` (optional): Max results (default: 10)

**Returns:**
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

### get_venue_details
Get detailed venue information.

**Parameters:**
- `venue_ref` (required): Venue reference number

**Returns:**
```json
{
  "name": "The Moon Under Water",
  "can_place_order": true,
  "venue_can_order": true,
  "sales_areas": [{"id": 789, "name": "Bar"}],
  "location": {"lat": 51.5074, "lng": -0.1278}
}
```

### get_menus
Get menus for a sales area.

**Parameters:**
- `venue_ref` (required): Venue reference
- `sales_area_id` (required): Sales area ID

**Returns:**
```json
[
  {"name": "Drinks", "can_order": true, "id": 12345},
  {"name": "Food", "can_order": true, "id": 12346}
]
```

### get_menu_details
Get detailed menu with items and prices.

**Parameters:**
- `menu_id` (required): Menu ID

**Returns:**
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

### get_drinks
Get drinks with price per unit analysis.

**Parameters:**
- `venue_ref` (required): Venue reference
- `sales_area_id` (required): Sales area ID

**Returns:**
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

## Data Types Summary

| Type | Description | Key Fields |
|------|-------------|------------|
| `HighLevelVenue` | Basic venue info | `name`, `venue_ref`, `address` |
| `DetailedVenue` | Extended venue info | `sales_areas`, `can_place_order` |
| `Address` | Full address | `line1`, `town`, `postcode`, `location` |
| `Location` | GPS coordinates | `latitude`, `longitude` |
| `HighLevelMenu` | Menu summary | `name`, `id`, `can_order` |
| `DetailedMenu` | Full menu data | `data` (contains categories/items) |
| `Drink` | Analyzed drink | `name`, `price`, `units`, `ppu` |

## Important Notes

1. **Price Format**: All prices in the API are in **pounds** (e.g., 1.62 = £1.62), not pence
2. **Unit Calculation**: UK standard - 1 unit = 10ml pure alcohol = (volume_ml × ABV%) / 1000
3. **Coordinates**: Latitude/Longitude in decimal degrees (WGS84)
4. **Sales Areas**: Dictionary access with `['id']`, not attribute access `.id`
5. **Synchronous API**: All functions are synchronous, no async/await needed
