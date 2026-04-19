from wetherspoons_api import venues, get_venue, get_drinks, get_menus, get_menu

def get_venue_by_name(venues_list, name):
    return next((v for v in venues_list if name.lower() in v.name.lower()), None)

def print_venue_food(venue, venue_details):
    print(f"\nFood Menus:")
    if not venue_details.sales_areas:
        print("  No sales areas available")
        return
    
    sales_area_id = venue_details.sales_areas[0].get('id')
    if not sales_area_id:
        print("  No sales area ID available")
        return
    
    try:
        menus = get_menus(venue_details, sales_area_id)
        food_menus = [m for m in menus if 'food' in m.name.lower() or m.name.lower() in ['burgers', 'pizzas', 'curry', 'steak', 'chicken']]
        
        if food_menus:
            print(f"  Found {len(food_menus)} food menu(s):")
            for menu in food_menus:
                print(f"    - {menu.name}")
                try:
                    detailed_menu = get_menu(menu)
                    categories = detailed_menu.data.get('categories', [])
                    print(f"      Categories: {len(categories)}")
                    
                    # Look for special offers or deals in category names
                    specials = [cat for cat in categories if any(word in cat.get('name', '').lower() for word in ['special', 'offer', 'deal', 'meal', 'combo'])]
                    if specials:
                        print(f"      Specials/Offers: {', '.join([s.get('name', '') for s in specials])}")
                except Exception as e:
                    print(f"      Error getting menu details: {e}")
        else:
            print(f"  Total menus: {len(menus)}")
            if menus:
                print(f"  Available menus: {', '.join([m.name for m in menus])}")
    except Exception as e:
        print(f"  Error fetching food menus: {e}")

def print_venue_drinks(venue, venue_name):
    if not venue:
        print(f"\n{venue_name} not found")
        return None
    
    print(f"\n{'='*60}")
    print(f"{venue.name}")
    print(f"{'='*60}")
    print(f"Venue ref: {venue.id}")
    
    venue_details = get_venue(venue)
    print_venue_food(venue, venue_details)
    
    drinks = get_drinks(venue)
    print(f"\nTotal drinks: {len(drinks)}")
    print("\nTop 5 best value drinks:")
    for i, d in enumerate(drinks[:5], 1):
        print(f"{i}. {d.name}")
        print(f"   Price: £{d.price/100:.2f}")
        print(f"   Units: {d.units:.2f}")
        print(f"   Price per unit: £{d.ppu/100:.2f}")
    
    return drinks

def main():
    print("Fetching all venues...")
    all_venues = venues()
    print(f"Found {len(all_venues)} venues")
    
    target_venues = ["watchman", "kings tun", "coronation hall"]
    venue_data = {}
    
    for target in target_venues:
        venue = get_venue_by_name(all_venues, target)
        drinks = print_venue_drinks(venue, target)
        if drinks:
            venue_data[venue.name] = drinks
    
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    
    for venue_name, drinks in venue_data.items():
        avg_price_per_unit = sum(d.ppu for d in drinks) / len(drinks) if drinks else 0
        print(f"\n{venue_name}:")
        print(f"  Total drinks: {len(drinks)}")
        print(f"  Avg price per unit: £{avg_price_per_unit/100:.2f}")
        print(f"  Best value drink: {drinks[0].name if drinks else 'N/A'} (£{drinks[0].ppu/100:.2f}/unit)")

if __name__ == "__main__":
    main()
