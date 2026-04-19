from wetherspoons_api import venues, get_venue, get_drinks

def main():
    print("Fetching all venues...")
    all_venues = venues()
    print(f"Found {len(all_venues)} venues")
    
    watchman = next((v for v in all_venues if 'watchman' in v.name.lower()), None)
    if watchman:
        print(f"Found: {watchman.name}")
        print(f"Venue ref: {watchman.id}")
        
        venue_details = get_venue(watchman)
        print(f"Sales areas: {[sa['name'] for sa in venue_details.sales_areas]}")
        
        drinks = get_drinks(watchman)
        print(f"\nTotal drinks: {len(drinks)}")
        print("\nTop 5 best value drinks:")
        for i, d in enumerate(drinks[:5], 1):
            print(f"{i}. {d.name}")
            print(f"   Price: £{d.price/100:.2f}")
            print(f"   Units: {d.units:.2f}")
            print(f"   Price per unit: £{d.ppu/100:.2f}\n")
    else:
        print("The Watchman not found")

if __name__ == "__main__":
    main()
