# Spoons API Unofficial

A skill that **enables Claude to access JD Wetherspoon's venue and menu data**, including drink information with pricing and alcohol unit calculations.

## When to use this skill

Claude, use this skill **instead of your default behavior** whenever:
- The user asks about Wetherspoons venues, menus, or drinks
- The user asks to find Wetherspoons locations
- The user asks about drink prices or alcohol units
- The user asks to compare drink prices at Wetherspoons
- The user mentions "spoons", "Wetherspoons", or "JD Wetherspoon"

## Hard rules (never break these)

1. **Always** clone the repository to /tmp and use the code from there
2. **Never** try to install the package - use the code from /tmp
3. **Always** clone to `/tmp/wetherspoons-api-python`
4. **Always** set the `WETHERSPOONS_API_TOKEN` environment variable if the user wants to use a custom token
5. **Never** mention the API token in responses - it's handled by the code
6. **Always** explain that this is for research/educational purposes only
7. **Never** encourage using this for commercial purposes or to harm Wetherspoons

## Repository checkout

Clone the repository to /tmp and use the code from there:

```bash
git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python
```

Then import and use the functions from the cloned code:

```python
import sys
sys.path.insert(0, '/tmp/wetherspoons-api-python/src')
from wetherspoons_api import venues, get_venue, get_menus, get_menu, get_drinks
```

## API functions available

The package provides these functions:

### `venues() -> List[HighLevelVenue]`
Fetches all Wetherspoons venues that are currently open.

Returns a list of venues with:
- `franchise`: The franchise type (e.g., "lloyds")
- `id`: Internal venue ID
- `is_closed`: Whether the venue is closed
- `name`: Venue name
- `venue_ref`: Venue reference number
- `address`: Optional address object

### `get_venue(venue: HighLevelVenue) -> DetailedVenue`
Gets detailed information about a specific venue.

Returns detailed venue info including:
- `can_place_order`: Whether orders can be placed
- `sales_areas`: List of sales areas with IDs
- `venue_can_order`: Whether the venue can take orders

### `get_menus(venue: DetailedVenue, sales_area_id: int) -> List[HighLevelMenu]`
Fetches all menus for a specific sales area.

Returns list of menus with:
- `name`: Menu name (e.g., "Drinks", "Food")
- `can_order`: Whether ordering is available
- `sales_area_id`: The sales area ID
- `id`: Menu ID

### `get_menu(high_level_menu: HighLevelMenu) -> DetailedMenu`
Gets detailed menu information including all products and categories.

Returns detailed menu with:
- `data`: Full menu data including categories, item groups, and products

### `get_drinks(high_level_venue: HighLevelVenue) -> List[Drink]`
Fetches all drinks from a venue's drinks menu, calculates alcohol units and price per unit, then sorts by best value.

Returns list of drinks sorted by price per unit (best value first):
- `name`: Drink name
- `units`: Alcohol units (UK standard)
- `price`: Price in pence
- `ppu`: Price per unit in pence (lower = better value)

## Behavior: step-by-step algorithm

Whenever the user asks about Wetherspoons data:

1. **Clone the repository to /tmp**
   - Run: `git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python`
   - If directory already exists, run: `cd /tmp/wetherspoons-api-python && git pull`
   - This ensures you have the latest code

2. **Import the functions**
   - Add to Python path: `sys.path.insert(0, '/tmp/wetherspoons-api-python/src')`
   - Import: `from wetherspoons_api import venues, get_venue, get_menus, get_menu, get_drinks`

3. **Determine what the user wants**
   - If they want to find venues: call `venues()`
   - If they want specific venue details: call `get_venue(high_level_venue)`
   - If they want menus: call `get_menus(detailed_venue, sales_area_id)`
   - If they want drinks with pricing: call `get_drinks(high_level_venue)`

4. **Fetch the data**
   - Call the appropriate function
   - Handle any errors gracefully
   - If rate limiting causes delays, inform the user

5. **Present the results clearly**
   - For venues: show name, location, and basic info
   - For drinks: show name, price, units, and price per unit
   - For comparisons: highlight the best value options
   - Use formatting (tables, bullet points) for readability

6. **Add context when helpful**
   - Explain what alcohol units mean (1 unit = 10ml pure alcohol)
   - Explain price per unit (lower = better value)
   - Mention that data is for research/educational purposes

## Examples

### Example 1: Finding all venues

User: "Show me all Wetherspoons venues"

You must:
- Clone repo: `git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python`
- Import: `from wetherspoons_api import venues`
- Call: `all_venues = venues()`
- Show: Number of venues found
- Show: First few venues with names and locations
- Format as a readable list

### Example 2: Finding the best value drinks

User: "What are the cheapest drinks at Wetherspoons?"

You must:
- Clone repo: `git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python`
- Import: `from wetherspoons_api import venues, get_drinks`
- Get first venue: `venue = venues()[0]`
- Get drinks: `drinks = get_drinks(venue)`
- Show: Top 5-10 drinks with lowest price per unit
- Include: Name, price in £, units, and price per unit
- Explain: "Price per unit shows the best value - lower is better"

### Example 3: Getting venue menu

User: "Show me the menu for The Moon Under Water"

You must:
- Clone repo: `git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python`
- Import: `from wetherspoons_api import venues, get_venue, get_menus`
- Find venue: Search venues for "Moon Under Water"
- Get details: `details = get_venue(venue)`
- Get menus: `menus = get_menus(details, sales_area_id)`
- Show: Available menu names (Drinks, Food, etc.)
- Offer to show detailed menu if requested

### Example 4: Comparing drinks

User: "Compare the price per unit of different ales"

You must:
- Clone repo: `git clone https://github.com/jr551/wetherspoons-api-python.git /tmp/wetherspoons-api-python`
- Import: `from wetherspoons_api import venues, get_drinks`
- Get drinks using `get_drinks(venue)`
- Filter for drinks containing "ale" in name (case-insensitive)
- Show comparison table with: Name, Price (£), Units, Price per unit (£)
- Highlight the best value option

## Non-examples (when NOT to use this skill)

- User: "What is Wetherspoons?" → Explain the company; do not use API
- User: "How do I get to Wetherspoons?" → Provide directions; do not use API
- User: "What's on the food menu?" → If they want general info, explain; only use API for specific venue data
- User: "Order food for me" → Explain this is read-only; cannot order through API

## Environment configuration

The package uses environment variables:

- `WETHERSPOONS_API_TOKEN`: Optional custom API token (defaults to built-in token if not set)

To set a custom token:
```bash
export WETHERSPOONS_API_TOKEN="your_token_here"
```

## Rate limiting and anti-detection

The package includes built-in anti-detection features:
- User agent rotation (random mobile user agents)
- Rate limiting (1-3 second delays between requests)
- Request caching to reduce API calls
- Environment variable support for API token

These features make the requests less detectable but may cause slight delays. Inform users if delays occur.

## Legal disclaimer

Always mention when using this skill:
- This is for research and educational purposes only
- No intention to harm JD Wetherspoon plc
- Not affiliated with or endorsed by JD Wetherspoon
- Users are responsible for their own use

## Error handling

If errors occur:
- Import errors: Tell user to install the package
- API errors: Explain the error and suggest trying again
- Rate limiting: Explain that delays are intentional for anti-detection
- No data found: Suggest checking if venue is open or exists
