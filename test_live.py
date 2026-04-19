"""Live test of the Python Wetherspoons API implementation"""

from wetherspoons_api import venues, get_venue, get_drinks

print("Testing Wetherspoons API (Python)...\n")

try:
    # Test 1: Get all venues
    print("1. Fetching all venues...")
    all_venues = venues()
    print(f"   Found {len(all_venues)} venues")
    print(f"   First venue: {all_venues[0].name} (ID: {all_venues[0].id})\n")

    # Test 2: Get venue details
    print("2. Getting venue details...")
    first_venue = all_venues[0]
    venue_details = get_venue(first_venue)
    print(f"   Venue: {venue_details.name}")
    print(f"   Can place order: {venue_details.can_place_order}")
    print(f"   Sales areas: {len(venue_details.sales_areas)}\n")

    # Test 3: Get drinks with price analysis
    print("3. Getting drinks with price per unit analysis...")
    drinks = get_drinks(first_venue)
    print(f"   Found {len(drinks)} drinks")
    
    if drinks:
        print("\n   Top 5 best value drinks:")
        for i, drink in enumerate(drinks[:5], 1):
            print(f"   {i}. {drink.name}")
            print(f"      Price: £{drink.price / 100:.2f}")
            print(f"      Units: {drink.units:.2f}")
            print(f"      Price per unit: £{drink.ppu / 100:.2f}\n")

    print("✅ All tests passed!")
except Exception as error:
    print(f"❌ Test failed: {error}")
    import traceback
    traceback.print_exc()
