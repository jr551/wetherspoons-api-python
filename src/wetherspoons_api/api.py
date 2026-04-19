"""Core API functions for Wetherspoons API"""

import json
import re
import requests
from typing import List, Optional
from .models import (
    HighLevelVenue,
    DetailedVenue,
    HighLevelMenu,
    DetailedMenu,
    Drink,
    Address,
    Location,
    Country,
)

API_ENDPOINT = "https://ca.jdw-apps.net/api/v0.1"
API_HEADERS = {
    "Authorization": "Bearer 1|SFS9MMnn5deflq0BMcUTSijwSMBB4mc7NSG2rOhqb2765466",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
}


def _request(path: str) -> dict:
    """Make a request to the Wetherspoons API"""
    response = requests.get(f"{API_ENDPOINT}{path}", headers=API_HEADERS)
    response.raise_for_status()
    return response.json()


def _parse_address(address_data: dict) -> Optional[Address]:
    """Parse address data from API response"""
    if not address_data:
        return None
    
    location_data = address_data.get("location")
    location = None
    if location_data:
        location = Location(**location_data)
    
    country_data = address_data.get("country")
    country = None
    if country_data:
        country = Country(**country_data)
    
    return Address(
        line1=address_data.get("line1"),
        line2=address_data.get("line2"),
        line3=address_data.get("line3"),
        town=address_data.get("town"),
        county=address_data.get("county"),
        postcode=address_data.get("postcode"),
        country=country,
        location=location,
    )


def venues() -> List[HighLevelVenue]:
    """Fetch all Wetherspoons venues"""
    # Fetch globals to filter open venues
    globals_response = requests.get(
        "https://oandp-appmgr-prod.s3.eu-west-2.amazonaws.com/global.json"
    )
    globals_response.raise_for_status()
    globals_data = globals_response.json()
    
    open_venue_ids = {v["identifier"] for v in globals_data.get("venues", [])}
    
    # Fetch venues from API
    response = _request("/venues")
    venues_data = response.get("data", [])
    
    # Filter to only open venues
    open_venues = []
    for venue_data in venues_data:
        if venue_data.get("venueRef") in open_venue_ids:
            address = _parse_address(venue_data.get("address"))
            venue_data["address"] = address
            open_venues.append(HighLevelVenue(**venue_data))
    
    return open_venues


def get_venue(venue: HighLevelVenue) -> DetailedVenue:
    """Get detailed information about a specific venue"""
    response = _request(f"/venues/{venue.venue_ref}")
    venue_data = response.get("data", {})
    
    address = _parse_address(venue_data.get("address"))
    venue_data["address"] = address
    
    return DetailedVenue(**venue_data)


def get_menus(venue: DetailedVenue, sales_area_id: int) -> List[HighLevelMenu]:
    """Fetch all menus for a specific sales area in a venue"""
    response = _request(
        f"/{venue.franchise}/venues/{venue.venue_ref}/sales-areas/{sales_area_id}/menus"
    )
    menus_data = response.get("data", [])
    
    return [HighLevelMenu(**menu_data) for menu_data in menus_data]


def get_menu(high_level_menu: HighLevelMenu) -> DetailedMenu:
    """Get detailed menu information including all products and categories"""
    response = _request(
        f"/{high_level_menu.franchise}/venues/{high_level_menu.venue_ref}"
        f"/sales-areas/{high_level_menu.sales_area_id}/menus/{high_level_menu.id}"
    )
    return DetailedMenu(**response)


def _strength_and_volume_to_units(strength: float, volume: float) -> float:
    """Calculate alcohol units from strength (ABV) and volume (ml)"""
    return (strength * volume) / 1000


def get_drinks(high_level_venue: HighLevelVenue) -> List[Drink]:
    """
    Fetch all drinks from a venue's drinks menu, 
    calculate alcohol units and price per unit, then sort by best value.
    """
    detailed_venue = get_venue(high_level_venue)
    
    if not detailed_venue.sales_areas:
        return []
    
    sales_area = detailed_venue.sales_areas[0]
    sales_area_id = sales_area.get("id")
    
    if not sales_area_id:
        return []
    
    menus = get_menus(detailed_venue, sales_area_id)
    
    # Find the drinks menu
    drinks_menu = None
    for menu in menus:
        if menu.name == "Drinks":
            drinks_menu = menu
            break
    
    if not drinks_menu:
        return []
    
    menu_data = get_menu(drinks_menu)
    
    # Convert menu to flat array of drinks
    products_map = {}
    
    for category in menu_data.data.get("categories", []):
        for item_group in category.get("itemGroups", []):
            for item in item_group.get("items", []):
                if item.get("itemType") == "product":
                    # Skip out of stock
                    if item.get("isOutOfStock"):
                        continue
                    products_map[item["id"]] = item
    
    drinks = []
    
    for product in products_map.values():
        description = product.get("description", "")
        
        # Parse ABV
        strength_matches = re.search(r"(\d?\d?\.?\d?\d%)\s?ABV", description)
        strength = None
        if strength_matches:
            strength = float(strength_matches.group(1).rstrip("%"))
        
        # Parse volume from description
        volume_description_matches = re.search(r"(\d?\d\d)ml", description)
        volume_description = None
        if volume_description_matches:
            volume_description = float(volume_description_matches.group(1))
        
        best_portion = None
        best_ppu = float("inf")
        best_units = 0.0
        
        portion_options = product.get("options", {}).get("portion", {}).get("options", [])
        
        for portion in portion_options:
            label = portion.get("label", "")
            units = None
            
            # Parse volume from portion label
            volume_matches = re.search(r"(\d?\d\d)ml", label)
            volume = None
            if volume_matches and volume_matches.group(1):
                volume = float(volume_matches.group(1))
            
            # Parse units from portion label
            units_matches = re.search(r"(\d?\.?\d?\d) unit", label)
            if units_matches and units_matches.group(1):
                units = float(units_matches.group(1))
            
            # Calculate units based on portion type
            if label == "Pint" and strength:
                units = _strength_and_volume_to_units(strength, 568)
            elif label in ["Half pint", "Half Pint", "Half"] and strength is not None:
                units = _strength_and_volume_to_units(strength, 284)
            elif strength is not None and volume:
                units = _strength_and_volume_to_units(strength, volume)
            elif strength is not None and volume_description:
                units = _strength_and_volume_to_units(strength, volume_description)
            elif strength is not None and label == "Single":
                units = _strength_and_volume_to_units(strength, 25)
            elif strength is not None and label == "Double":
                units = _strength_and_volume_to_units(strength, 50)
            
            if units is not None and units > 0:
                price_value = portion.get("value", {}).get("price", {}).get("value", 0)
                ppu = price_value / units
                
                if ppu < best_ppu:
                    best_ppu = ppu
                    best_portion = portion
                    best_units = units
        
        if best_portion:
            drinks.append(
                Drink(
                    name=product.get("name", ""),
                    units=best_units,
                    ppu=best_ppu,
                    product_id=product.get("id"),
                    price=best_portion.get("value", {}).get("price", {}).get("value", 0),
                )
            )
    
    # Sort by price per unit (best value first)
    drinks.sort(key=lambda x: x.ppu)
    
    return drinks
